#!/usr/bin/env bash
# ============================================================================
# aws-deploy-services.sh
# Registra task definitions y crea/actualiza services ECS Fargate.
# Backend y app-pagos usan Service Discovery (Cloud Map) para DNS interno.
# Frontend recibe la IP pública del backend al desplegarse.
# ============================================================================

set -e

if [ ! -f "aws-env.sh" ]; then
  echo "ERROR: aws-env.sh no existe. Corre primero aws-setup.sh"
  exit 1
fi
source aws-env.sh

# Cargar credenciales MP desde .env
if [ -f "../.env" ]; then
  set -a; source ../.env; set +a
elif [ -f ".env" ]; then
  set -a; source .env; set +a
else
  echo "ERROR: .env no encontrado"
  exit 1
fi

export MP_SUCCESS_URL="${MP_SUCCESS_URL:-https://www.mercadopago.cl/success}"
export MP_FAILURE_URL="${MP_FAILURE_URL:-https://www.mercadopago.cl/failure}"
export MP_PENDING_URL="${MP_PENDING_URL:-https://www.mercadopago.cl/pending}"
export MP_WEBHOOK_URL="${MP_WEBHOOK_URL:-}"

export APP_PAGOS_URL="http://app-pagos.${NAMESPACE_NAME}:8002"
export API_URL="${API_URL:-http://placeholder:8000}"

SUBNETS_ARRAY=$(echo "$SUBNETS" | sed 's/,/","/g')

mkdir -p .rendered
for svc in app-pagos backend frontend; do
  echo "==> Renderizando + registrando task-${svc}"
  envsubst < "task-definitions/task-${svc}.json" > ".rendered/task-${svc}.json"
  aws ecs register-task-definition \
    --cli-input-json "file://.rendered/task-${svc}.json" \
    --region "$AWS_REGION" >/dev/null
done

service_exists() {
  aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$1" \
    --region "$AWS_REGION" \
    --query 'services[?status==`ACTIVE`].serviceName' --output text 2>/dev/null | grep -q .
}

create_or_update_service() {
  local svc=$1
  local sd_arn=$2  # opcional
  local task_family="${PROJECT_NAME}-${svc}"
  local full_name="${PROJECT_NAME}-${svc}-svc"

  if service_exists "$full_name"; then
    echo "==> Actualizando service: $full_name"
    aws ecs update-service \
      --cluster "$CLUSTER_NAME" --service "$full_name" \
      --task-definition "$task_family" \
      --force-new-deployment \
      --region "$AWS_REGION" >/dev/null
  else
    echo "==> Creando service: $full_name"
    local sd_arg=""
    [ -n "$sd_arn" ] && sd_arg="--service-registries registryArn=$sd_arn"

    aws ecs create-service \
      --cluster "$CLUSTER_NAME" \
      --service-name "$full_name" \
      --task-definition "$task_family" \
      --desired-count 1 \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[\"${SUBNETS_ARRAY}\"],securityGroups=[\"$SG_ID\"],assignPublicIp=ENABLED}" \
      $sd_arg \
      --region "$AWS_REGION" >/dev/null
  fi
}

create_or_update_service "app-pagos" "$SD_APP_PAGOS_ARN"
create_or_update_service "backend"   "$SD_BACKEND_ARN"

echo "==> Esperando 45s a que backend levante..."
sleep 45

BACKEND_TASK_ARN=$(aws ecs list-tasks \
  --cluster "$CLUSTER_NAME" --service-name "${PROJECT_NAME}-backend-svc" \
  --region "$AWS_REGION" --query 'taskArns[0]' --output text)

BACKEND_PUBLIC_IP=""
if [ "$BACKEND_TASK_ARN" != "None" ] && [ -n "$BACKEND_TASK_ARN" ]; then
  ENI_ID=$(aws ecs describe-tasks \
    --cluster "$CLUSTER_NAME" --tasks "$BACKEND_TASK_ARN" \
    --region "$AWS_REGION" \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

  if [ -n "$ENI_ID" ]; then
    BACKEND_PUBLIC_IP=$(aws ec2 describe-network-interfaces \
      --network-interface-ids "$ENI_ID" --region "$AWS_REGION" \
      --query 'NetworkInterfaces[0].Association.PublicIp' --output text 2>/dev/null || echo "")
  fi
fi

if [ -n "$BACKEND_PUBLIC_IP" ] && [ "$BACKEND_PUBLIC_IP" != "None" ]; then
  export API_URL="http://${BACKEND_PUBLIC_IP}:8000"
  echo "==> API_URL para frontend: $API_URL"
  envsubst < "task-definitions/task-frontend.json" > ".rendered/task-frontend.json"
  aws ecs register-task-definition \
    --cli-input-json "file://.rendered/task-frontend.json" \
    --region "$AWS_REGION" >/dev/null
else
  echo "WARN: No se pudo obtener IP del backend (talvez aún no levanta). Frontend usa placeholder."
fi

create_or_update_service "frontend" ""

echo ""
echo "============================================================"
echo "  SERVICES DESPLEGADOS"
echo "============================================================"
echo "  Cluster:        $CLUSTER_NAME"
echo "  Backend IP:     ${BACKEND_PUBLIC_IP:-aún no asignada}"
echo "  API_URL:        $API_URL"
echo ""
echo "  Para ver IPs y estado:  ./aws-show-ips.sh"
echo "  Consola: https://${AWS_REGION}.console.aws.amazon.com/ecs/v2/clusters/${CLUSTER_NAME}/services?region=${AWS_REGION}"
echo "============================================================"
