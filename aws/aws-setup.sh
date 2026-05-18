#!/usr/bin/env bash
# ============================================================================
# aws-setup.sh
# Crea infraestructura AWS base: ECR, ECS cluster, log group, IAM role,
# security group, namespace de Cloud Map (Service Discovery).
# ============================================================================

# Evita que Git Bash en Windows convierta paths tipo /ecs/... a C:/Program Files/Git/ecs/...
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"

set -e

# -------- CONFIG --------
export AWS_REGION="${AWS_REGION:-us-east-2}"
export PROJECT_NAME="${PROJECT_NAME:-ev2-cloud}"
export CLUSTER_NAME="${PROJECT_NAME}-cluster"
export LOG_GROUP="/ecs/${PROJECT_NAME}"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "==> Account: $ACCOUNT_ID  Region: $AWS_REGION"

# -------- 1. ECR REPOS --------
for repo in frontend backend app-pagos; do
  REPO_NAME="${PROJECT_NAME}-${repo}"
  echo "==> Creando ECR repo: $REPO_NAME"
  aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" >/dev/null 2>&1 || \
    aws ecr create-repository \
      --repository-name "$REPO_NAME" \
      --image-scanning-configuration scanOnPush=true \
      --region "$AWS_REGION" >/dev/null
done

# -------- 2. CLOUDWATCH LOG GROUP --------
echo "==> Creando log group: $LOG_GROUP"
aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --region "$AWS_REGION" \
  --query 'logGroups[?logGroupName==`'"$LOG_GROUP"'`]' --output text | grep -q . || \
  aws logs create-log-group --log-group-name "$LOG_GROUP" --region "$AWS_REGION"

# -------- 3. IAM ROLE: ecsTaskExecutionRole --------
echo "==> Verificando ecsTaskExecutionRole"
if ! aws iam get-role --role-name ecsTaskExecutionRole >/dev/null 2>&1; then
  aws iam create-role --role-name ecsTaskExecutionRole \
    --assume-role-policy-document '{
      "Version":"2012-10-17",
      "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
    }' >/dev/null
  aws iam attach-role-policy --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
fi
EXEC_ROLE_ARN=$(aws iam get-role --role-name ecsTaskExecutionRole --query 'Role.Arn' --output text)

# -------- 4. CLUSTER ECS --------
echo "==> Creando cluster: $CLUSTER_NAME"
aws ecs describe-clusters --clusters "$CLUSTER_NAME" --region "$AWS_REGION" \
  --query 'clusters[?status==`ACTIVE`]' --output text | grep -q . || \
  aws ecs create-cluster --cluster-name "$CLUSTER_NAME" --region "$AWS_REGION" >/dev/null

# -------- 5. RED: VPC default + subnets + SG --------
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" \
  --query 'Vpcs[0].VpcId' --output text --region "$AWS_REGION")
echo "==> VPC default: $VPC_ID"

SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[].SubnetId' --output text --region "$AWS_REGION" | tr '\t' ',')
echo "==> Subnets: $SUBNETS"

SG_NAME="${PROJECT_NAME}-sg"
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' --output text --region "$AWS_REGION" 2>/dev/null || echo "None")

if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
  echo "==> Creando security group $SG_NAME"
  SG_ID=$(aws ec2 create-security-group \
    --group-name "$SG_NAME" \
    --description "EV2 Cloud security group" \
    --vpc-id "$VPC_ID" \
    --region "$AWS_REGION" \
    --query 'GroupId' --output text)

  for port in 80 8000 8002 3306; do
    aws ec2 authorize-security-group-ingress \
      --group-id "$SG_ID" \
      --protocol tcp --port "$port" --cidr 0.0.0.0/0 \
      --region "$AWS_REGION" >/dev/null 2>&1 || true
  done
fi
echo "==> Security group: $SG_ID"

# -------- 6. SERVICE DISCOVERY (Cloud Map) --------
NAMESPACE_NAME="${PROJECT_NAME}.local"
echo "==> Verificando namespace de Service Discovery: $NAMESPACE_NAME"
NAMESPACE_ID=$(aws servicediscovery list-namespaces \
  --region "$AWS_REGION" \
  --query "Namespaces[?Name=='${NAMESPACE_NAME}'].Id" --output text 2>/dev/null || echo "")

if [ -z "$NAMESPACE_ID" ] || [ "$NAMESPACE_ID" == "None" ]; then
  echo "==> Creando namespace privado de Cloud Map"
  OP_ID=$(aws servicediscovery create-private-dns-namespace \
    --name "$NAMESPACE_NAME" \
    --vpc "$VPC_ID" \
    --region "$AWS_REGION" \
    --query 'OperationId' --output text)

  echo "    Esperando operación $OP_ID..."
  for i in {1..30}; do
    STATUS=$(aws servicediscovery get-operation --operation-id "$OP_ID" \
      --region "$AWS_REGION" --query 'Operation.Status' --output text)
    [ "$STATUS" == "SUCCESS" ] && break
    sleep 3
  done

  NAMESPACE_ID=$(aws servicediscovery list-namespaces \
    --region "$AWS_REGION" \
    --query "Namespaces[?Name=='${NAMESPACE_NAME}'].Id" --output text)
fi
echo "==> Namespace ID: $NAMESPACE_ID"

for svc in backend app-pagos; do
  SD_NAME="${svc}"
  SD_ID=$(aws servicediscovery list-services \
    --region "$AWS_REGION" \
    --filters "Name=NAMESPACE_ID,Values=$NAMESPACE_ID,Condition=EQ" \
    --query "Services[?Name=='${SD_NAME}'].Id" --output text 2>/dev/null || echo "")

  if [ -z "$SD_ID" ] || [ "$SD_ID" == "None" ]; then
    echo "==> Creando SD service: $SD_NAME"
    aws servicediscovery create-service \
      --name "$SD_NAME" \
      --namespace-id "$NAMESPACE_ID" \
      --dns-config "NamespaceId=$NAMESPACE_ID,RoutingPolicy=MULTIVALUE,DnsRecords=[{Type=A,TTL=10}]" \
      --health-check-custom-config "FailureThreshold=1" \
      --region "$AWS_REGION" >/dev/null
  fi
done

SD_BACKEND_ARN=$(aws servicediscovery list-services \
  --region "$AWS_REGION" \
  --filters "Name=NAMESPACE_ID,Values=$NAMESPACE_ID,Condition=EQ" \
  --query "Services[?Name=='backend'].Arn" --output text)
SD_APP_PAGOS_ARN=$(aws servicediscovery list-services \
  --region "$AWS_REGION" \
  --filters "Name=NAMESPACE_ID,Values=$NAMESPACE_ID,Condition=EQ" \
  --query "Services[?Name=='app-pagos'].Arn" --output text)

# -------- 7. EXPORTAR --------
cat > aws-env.sh <<EOF
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"
export AWS_REGION="$AWS_REGION"
export ACCOUNT_ID="$ACCOUNT_ID"
export CLUSTER_NAME="$CLUSTER_NAME"
export EXEC_ROLE_ARN="$EXEC_ROLE_ARN"
export VPC_ID="$VPC_ID"
export SUBNETS="$SUBNETS"
export SG_ID="$SG_ID"
export PROJECT_NAME="$PROJECT_NAME"
export LOG_GROUP="$LOG_GROUP"
export NAMESPACE_NAME="$NAMESPACE_NAME"
export SD_BACKEND_ARN="$SD_BACKEND_ARN"
export SD_APP_PAGOS_ARN="$SD_APP_PAGOS_ARN"
EOF

echo ""
echo "============================================================"
echo "  INFRAESTRUCTURA BASE CREADA"
echo "============================================================"
echo "  Region:       $AWS_REGION"
echo "  Cluster:      $CLUSTER_NAME"
echo "  SG:           $SG_ID"
echo "  Subnets:      $SUBNETS"
echo "  Exec Role:    $EXEC_ROLE_ARN"
echo "  ECR repos:    ${PROJECT_NAME}-frontend, ${PROJECT_NAME}-backend, ${PROJECT_NAME}-app-pagos"
echo ""
echo "  Variables exportadas en: aws-env.sh"
echo "============================================================"
