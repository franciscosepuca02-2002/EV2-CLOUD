# PASOS PARA APLICAR LOS CAMBIOS

## Antes de tocar nada

### 0. Sacar el .env del repo (CRÍTICO)
Tu `.env` con credenciales MP está en GitHub. Borra del tracking:

```bash
cd EV2-CLOUD
git rm --cached .env
echo ".env" >> .gitignore   # ya viene en el nuevo .gitignore
git commit -m "remove .env from tracking"
```

Las credenciales seguirán en el historial. Para esta entrega da igual (son de prueba), pero anótalo para el futuro.

---

## 1. Aplicar archivos generados

Descomprime el zip que te entrego y copia/sobrescribe sobre tu repo local. Estructura final:

```
EV2-CLOUD/
├── .github/workflows/deploy.yml   ← NUEVO
├── .gitignore                     ← NUEVO/sobrescribir
├── .env.example                   ← NUEVO
├── README.md                      ← sobrescribir
├── docker-compose.yml             ← sobrescribir
├── aws/                           ← NUEVO (carpeta entera)
├── backend/
│   ├── Dockerfile                 ← sobrescribir
│   ├── requirements.txt           ← sobrescribir (estaba UTF-16)
│   ├── main.py                    ← sobrescribir
│   ├── .dockerignore              ← NUEVO
│   ├── database/database.py       ← sobrescribir
│   ├── models/
│   │   ├── user.py                ← sobrescribir
│   │   ├── producto.py            ← NUEVO
│   │   └── pedido.py              ← NUEVO
│   ├── routers/
│   │   ├── auth.py                ← sobrescribir
│   │   ├── productos.py           ← NUEVO
│   │   └── pagos.py               ← NUEVO
│   └── schemas/user.py            ← sobrescribir
├── frontend/
│   ├── Dockerfile                 ← sobrescribir (era ng serve, ahora nginx)
│   ├── nginx.conf                 ← NUEVO
│   ├── entrypoint.sh              ← NUEVO
│   ├── .dockerignore              ← NUEVO
│   └── src/
│       ├── assets/config.json     ← NUEVO
│       └── app/
│           ├── app.config.ts      ← sobrescribir
│           ├── services/          ← sobrescribir todo
│           │   ├── auth.ts
│           │   ├── carrito.ts
│           │   ├── pago.ts
│           │   ├── producto.ts
│           │   └── config.service.ts ← NUEVO
│           ├── components/navbar/
│           │   ├── navbar.ts      ← sobrescribir
│           │   └── navbar.html    ← sobrescribir
│           └── pages/
│               ├── login/         ← sobrescribir login.ts, login.html, login.css
│               ├── register/      ← sobrescribir register.ts, register.html, register.css
│               ├── pago/          ← sobrescribir pago.ts, pago.html, pago.css
│               ├── productos/     ← sobrescribir productos.ts, productos.html
│               └── carrito/       ← sobrescribir carrito.ts, carrito.html
└── app-pagos/                     ← sin cambios
```

NO tocar: `app-pagos/`, `frontend/node_modules/`, `frontend/public/`, `backend/venv/`, archivos `.spec.ts`.

---

## 2. Probar local antes de subir

```bash
docker compose down -v   # limpia DB anterior
docker compose up --build
```

Probar:
- http://localhost:4200 → ver navbar, hacer registro → login
- Agregar productos al carrito → ir a pago → debería redirigir a Mercado Pago
- http://localhost:8000/docs → ver endpoints

Si todo funciona, hacer commit + push:

```bash
git add .
git commit -m "Fase 1: backend con BD, frontend completo, Dockerfile producción"
git push origin main
```

---

## 3. Configurar AWS

### a) Crear IAM user para CI/CD
1. AWS Console → IAM → Users → Create user → `ev2-cloud-ci`
2. Pestaña Permissions → Add permissions → Attach policies directly → Create policy
3. Pegar el JSON del README (sección "IAM user mínimo")
4. Pestaña Security credentials → Create access key → Application running outside AWS
5. **Guardar el Access Key ID y Secret Access Key**

### b) Configurar AWS CLI localmente
```bash
aws configure
# AWS Access Key ID: (el del paso anterior)
# AWS Secret Access Key: (el del paso anterior)
# Default region: us-east-2
# Default output: json
```

### c) Crear infra base
```bash
cd aws
chmod +x *.sh
./aws-setup.sh
```

Debería tardar ~1 min y crear todo. Si algo falla por permisos, dale más perms al IAM user temporalmente (admin para hoy, restringir después).

### d) Agregar secrets al repo GitHub
1. GitHub repo → Settings → Secrets and variables → Actions
2. New repository secret:
   - `AWS_ACCESS_KEY_ID` → el del paso a
   - `AWS_SECRET_ACCESS_KEY` → el del paso a

### e) Triggear el pipeline
Cualquier push a `main` lo dispara. O Actions → Build & Deploy to AWS → Run workflow.

El pipeline:
- Buildea las 3 imágenes
- Las pushea a ECR
- Hace force-new-deployment (la primera vez los services aún no existen, pasa)

### f) Crear los services (primera vez)
Después de que el pipeline haya subido las imágenes a ECR:
```bash
cd aws
./aws-deploy-services.sh
```

### g) Ver las IPs
```bash
./aws-show-ips.sh
```

Tienes 3 URLs: frontend, backend, app-pagos. Abre la del frontend.

---

## 4. Demo CI/CD en vivo (para la presentación)

1. Cambiar el título del navbar (en `frontend/src/app/components/navbar/navbar.html`)
2. `git commit -am "demo cambio en navbar"` + `git push`
3. GitHub → Actions → mostrar el workflow corriendo
4. Cuando termine, refrescar URL del frontend → cambio visible

---

## 5. Si algo falla

**Backend no levanta:**
```bash
docker logs backend
```
Si es error de BD, esperar 30s y reintentar (MySQL tarda en arrancar).

**Frontend muestra placeholder API URL:**
Revisar `config.json` en el contenedor:
```bash
docker exec frontend cat /usr/share/nginx/html/assets/config.json
```

**En AWS, tasks que se reinician:**
```bash
aws ecs describe-services --cluster ev2-cloud-cluster --services ev2-cloud-backend-svc --region us-east-2
```
Ver mensaje de error.

**Service no se actualiza:**
```bash
aws ecs update-service --cluster ev2-cloud-cluster --service ev2-cloud-backend-svc --force-new-deployment --region us-east-2
```
