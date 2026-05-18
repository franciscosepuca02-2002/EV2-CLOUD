# EV2 Cloud — Tienda con microservicios

Sistema de venta online con arquitectura de microservicios desplegado en AWS ECS Fargate.

## Arquitectura

```
Usuario → Frontend (Angular + nginx) → Backend (FastAPI + MySQL) → app-pagos (FastAPI + Mercado Pago)
```

- **Frontend** (puerto 80): Angular 21, build estático servido por nginx, runtime config vía `assets/config.json`
- **Backend** (puerto 8000): FastAPI, auth con bcrypt, productos/pedidos persistidos en MySQL
- **app-pagos** (puerto 8002): FastAPI, integración con Mercado Pago (checkout + pago directo + webhook)
- **MySQL** (puerto 3306): contenedor sidecar de backend en ECS, contenedor independiente en local

En AWS:
- Backend y app-pagos se comunican vía **AWS Cloud Map** (Service Discovery): `app-pagos.ev2-cloud.local`
- Frontend recibe la IP pública del backend al desplegarse, vía `API_URL` que el entrypoint inyecta en `config.json`

---

## Desarrollo local

```bash
# Configura tus credenciales MP en .env (ver .env.example)
docker-compose up --build
```

- Frontend: http://localhost:4200
- Backend: http://localhost:8000/docs
- app-pagos: http://localhost:8002/docs

---

## Despliegue en AWS

### Prerrequisitos
1. AWS CLI configurado: `aws configure` (en region `us-east-2`)
2. `jq` instalado (`sudo apt install jq` o equivalente)
3. Credenciales MP válidas en `.env`

### Paso 1 — Crear infraestructura base

```bash
cd aws
chmod +x *.sh
./aws-setup.sh
```

Crea:
- 3 repos ECR (`ev2-cloud-frontend`, `ev2-cloud-backend`, `ev2-cloud-app-pagos`)
- Cluster ECS `ev2-cloud-cluster`
- Log group CloudWatch `/ecs/ev2-cloud`
- IAM role `ecsTaskExecutionRole`
- Security group con puertos 80/8000/8002/3306 abiertos
- Namespace privado Cloud Map `ev2-cloud.local`

Genera `aws/aws-env.sh` con todas las variables.

### Paso 2 — Pushear imágenes a ECR

**Opción A (manual, primer push):**

```bash
source aws/aws-env.sh
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

for svc in frontend backend app-pagos; do
  docker build -t $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/ev2-cloud-$svc:latest ./$svc
  docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/ev2-cloud-$svc:latest
done
```

**Opción B (automático vía pipeline):** ver más abajo CI/CD.

### Paso 3 — Crear services ECS

```bash
cd aws
./aws-deploy-services.sh
```

Espera ~1 min. Al final muestra la IP pública del backend.

### Paso 4 — Obtener URLs públicas

```bash
cd aws
./aws-show-ips.sh
```

Muestra:
```
frontend: http://X.X.X.X:80
backend: http://Y.Y.Y.Y:8000
app-pagos: http://Z.Z.Z.Z:8002
```

Abre la URL del frontend en el navegador.

---

## CI/CD (GitHub Actions)

El pipeline `.github/workflows/deploy.yml`:

1. Buildea las 3 imágenes
2. Las pushea a ECR (tags `latest` y SHA del commit)
3. Hace `force-new-deployment` en los 3 services ECS

### Configuración de Secrets en GitHub

Settings → Secrets and variables → Actions → New repository secret:

| Secret | Valor |
|---|---|
| `AWS_ACCESS_KEY_ID` | clave de un IAM user con permisos ECR + ECS |
| `AWS_SECRET_ACCESS_KEY` | secret del mismo IAM user |

### IAM user mínimo para el pipeline

Crear un IAM user `ev2-cloud-ci` y attach inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "*"
    }
  ]
}
```

Generar Access keys → guardarlas como secrets.

---

## Demostrar CI/CD en vivo

1. Hacer un cambio simple (ej: cambiar el título del navbar)
2. `git commit -am "demo cambio"` && `git push origin main`
3. En GitHub: Actions → ver el workflow corriendo
4. Al terminar, refrescar la URL del frontend → cambio visible

---

## Estructura del proyecto

```
EV2-CLOUD/
├── .github/workflows/deploy.yml      # Pipeline CI/CD
├── aws/
│   ├── aws-setup.sh                  # Crea infra base
│   ├── aws-deploy-services.sh        # Despliega services
│   ├── aws-show-ips.sh               # Muestra IPs
│   └── task-definitions/             # JSON de task definitions
├── backend/                          # FastAPI + SQLAlchemy
├── frontend/                         # Angular + nginx
├── app-pagos/                        # FastAPI + Mercado Pago
├── docker-compose.yml                # Stack local
├── .env                              # Credenciales MP (NO versionar)
└── .gitignore
```

---

## Aspectos de seguridad

- Credenciales Mercado Pago en variables de entorno (en ECS pueden migrar a AWS Secrets Manager)
- `.env` excluido de git (ver `.gitignore`)
- Passwords con bcrypt en backend
- CORS abierto para demo; en producción restringir a dominio del frontend
- Security group abre solo los puertos necesarios

## Pendientes / mejoras

- Migrar BD a AWS RDS MySQL (más resiliente)
- Application Load Balancer + Route53 para tener DNS estable
- HTTPS con certificado ACM
- Secrets Manager para credenciales MP
- WAF en frente del ALB
