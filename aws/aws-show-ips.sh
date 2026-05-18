#!/usr/bin/env bash
# Muestra las IPs públicas de cada service ECS
set -e
source aws-env.sh

for svc in frontend backend app-pagos; do
  FULL="${PROJECT_NAME}-${svc}-svc"
  TASK=$(aws ecs list-tasks --cluster "$CLUSTER_NAME" --service-name "$FULL" \
    --region "$AWS_REGION" --query 'taskArns[0]' --output text 2>/dev/null)

  if [ "$TASK" == "None" ] || [ -z "$TASK" ]; then
    echo "$svc: (sin tarea activa)"
    continue
  fi

  ENI=$(aws ecs describe-tasks --cluster "$CLUSTER_NAME" --tasks "$TASK" \
    --region "$AWS_REGION" \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

  IP=$(aws ec2 describe-network-interfaces --network-interface-ids "$ENI" \
    --region "$AWS_REGION" \
    --query 'NetworkInterfaces[0].Association.PublicIp' --output text 2>/dev/null)

  case $svc in
    frontend) PORT=80 ;;
    backend)  PORT=8000 ;;
    app-pagos) PORT=8002 ;;
  esac

  echo "$svc: http://${IP}:${PORT}"
done
