# 💳 Microservicio de Pagos con MercadoPago

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12-green)
![Docker](https://img.shields.io/badge/docker-required-blue)
![MercadoPago](https://img.shields.io/badge/MercadoPago-API%20v1-009ee3)

Servicio simplificado para procesar pagos con tarjeta de crédito/débito utilizando la API de MercadoPago. Este servicio **NO** utiliza base de datos, solo procesa pagos y retorna el estado directamente desde MercadoPago.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Configuración Inicial](#-configuración-inicial)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Endpoints Disponibles](#-endpoints-disponibles)
- [Pruebas con Script Python](#-pruebas-con-script-python)
- [Tarjetas de Prueba](#-tarjetas-de-prueba)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Características

- ✅ Procesamiento de pagos directo con tarjeta (sin guardar)
- ✅ Integración completa con MercadoPago API v1
- ✅ Soporte para múltiples escenarios de pago (aprobado, rechazado, pendiente)
- ✅ Consulta de estado de pagos
- ✅ Cancelación de pagos
- ✅ Webhook para notificaciones de MercadoPago
- ✅ Sin base de datos (stateless)
- ✅ Dockerizado y listo para producción
- ✅ Logs detallados de todas las operaciones

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Python 3.8+** (solo para ejecutar el script de pruebas)
- **Cuenta de MercadoPago** con acceso a credenciales de prueba

### Verificar instalación de Docker

```bash
docker --version
docker-compose --version
```

---

## 🔧 Configuración Inicial

### **PASO 1: Obtener credenciales de MercadoPago**

1. Ingresa a tu cuenta de MercadoPago: https://www.mercadopago.cl
2. Ve a **Tus integraciones** → **Credenciales**
3. Copia las credenciales de **PRUEBA** (TEST):
   - `Access Token` (comienza con `TEST-`)
   - `Public Key` (comienza con `TEST-`)

⚠️ **IMPORTANTE**: Nunca uses credenciales de producción para pruebas.

### **PASO 2: Configurar variables de entorno**

Edita el archivo `.env` en la raíz del proyecto y agrega tus credenciales:

```bash
# .env
MP_ACCESS_TOKEN=TEST-tu-access-token-aqui
MP_PUBLIC_KEY=TEST-tu-public-key-aqui
MP_WEBHOOK_URL=
MP_SUCCESS_URL=https://www.mercadopago.cl/success
MP_FAILURE_URL=https://www.mercadopago.cl/failure
MP_PENDING_URL=https://www.mercadopago.cl/pending
```

## 🚀 Instalación y Ejecución

### **Opción 1: Usando Docker Compose (Recomendado)**

```bash
# 1. Clonar o navegar al directorio del proyecto
cd proyecto-microservicios

# 2. Asegurarse de que el archivo .env esté configurado
cat .env

# 3. Levantar el servicio
docker-compose up --build -d

# 4. Verificar que el contenedor esté corriendo
docker ps

# 5. Ver los logs
docker logs app-pagos -f
```

El servicio estará disponible en: **http://localhost:8002**

### **Opción 2: Ejecución local (sin Docker)**

```bash
# 1. Navegar al directorio del servicio
cd app-pagos

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Ejecutar el servicio
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### **Verificar que el servicio esté funcionando**

```bash
# Verificar salud del servicio
curl http://localhost:8002/health

# Respuesta esperada:
# {
#   "status": "healthy",
#   "service": "app-pagos",
#   "mercadopago_status": "ok"
# }
```

---

## 📡 Endpoints Disponibles

### **1. Health Check**

```http
GET /health
```

Verifica que el servicio esté funcionando y las credenciales estén configuradas.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "app-pagos",
  "mercadopago_status": "ok"
}
```

---

### **2. Procesar Pago Directo con Tarjeta**

```http
POST /pagos/directo/procesar
```

Procesa un pago directo con los datos de la tarjeta.

**Request Body:**
```json
{
  "id_usuario": 1,
  "numero_tarjeta": "4168818844447115",
  "mes_vencimiento": 11,
  "anio_vencimiento": 2030,
  "cvv": "123",
  "nombre_titular": "APRO",
  "email": "test@example.com",
  "descripcion": "Pago de prueba",
  "monto": 5000.0
}
```

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "message": "Pago procesado correctamente",
  "data": {
    "id_pago": 1000000,
    "estado": "PAGADO",
    "mp_payment_id": 1327140454,
    "external_reference": "USR1-20260512122915-0706cc05"
  }
}
```

**Estados posibles:**
- `PAGADO` - Pago aprobado
- `RECHAZADO` - Pago rechazado
- `PENDIENTE` - Pago pendiente de confirmación
- `CANCELADO` - Pago cancelado
- `EXPIRADO` - Pago expirado (después de 120 segundos)

---

### **3. Consultar Estado de Pago**

```http
GET /pagos/{id_pago}/estado
```

Consulta el estado actual de un pago.

**Ejemplo:**
```bash
curl http://localhost:8002/pagos/1000000/estado
```

**Respuesta:**
```json
{
  "id_pago": 1000000,
  "estado": "PAGADO"
}
```

---

### **4. Cancelar Pago**

```http
POST /pagos/{id_pago}/cancelar
```

Cancela un pago pendiente.

**Ejemplo:**
```bash
curl -X POST http://localhost:8002/pagos/1000000/cancelar
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Pago cancelado",
  "data": {
    "id_pago": 1000000,
    "estado": "CANCELADO"
  }
}
```

---

### **5. Webhook de MercadoPago**

```http
POST /pagos/webhook
```

Endpoint para recibir notificaciones de MercadoPago cuando cambia el estado de un pago.

---

## 🧪 Pruebas con Script Python

El proyecto incluye un script de prueba completo que valida todos los escenarios de pago.

### **Ejecutar el script de pruebas**

```bash
# Asegurarse de que el servicio esté corriendo
docker-compose up -d

# Ejecutar el script de pruebas
python3 test_pago_tarjeta.py
```

### **¿Qué hace el script?**

El script `test_pago_tarjeta.py` realiza las siguientes pruebas automáticas:

1. ✅ **Verificación del servicio** - Confirma que el servicio esté disponible
2. 💳 **Pago aprobado** - Prueba con tarjeta Visa y titular "APRO"
3. ❌ **Pago rechazado** - Prueba rechazo por fondos insuficientes (titular "FUND")
4. ⏳ **Pago pendiente** - Prueba pago pendiente (titular "CONT")
5. 🚫 **Pago rechazado general** - Prueba rechazo por error general (titular "OTHE")

### **Salida esperada del script**

```
================================================================================
🚀 INICIANDO PRUEBAS DE PAGOS CON MERCADOPAGO
================================================================================
✅ Servicio verificado y funcionando correctamente

================================================================================
📝 PRUEBA 1: Pago APROBADO con Visa Crédito
================================================================================
💳 Detalles del pago:
   ID Pago: 1000000
   Estado: PAGADO
   MP Payment ID: 1327140454
✅ ÉXITO: Estado obtenido 'PAGADO' coincide con esperado 'PAGADO'

[... más pruebas ...]

================================================================================
📊 RESUMEN DE PRUEBAS COMPLETADAS
================================================================================
✅ Todas las pruebas han sido ejecutadas
```

---

## 💳 Tarjetas de Prueba

MercadoPago proporciona tarjetas de prueba para simular diferentes escenarios de pago.

### **Tarjetas Disponibles**

| Tipo | Bandera | Número | CVV | Vencimiento |
|------|---------|--------|-----|-------------|
| Crédito | Mastercard | `5416 7526 0258 2580` | 123 | 11/30 |
| Crédito | Visa | `4168 8188 4444 7115` | 123 | 11/30 |
| Crédito | American Express | `3757 781744 61804` | 1234 | 11/30 |
| Débito | Mastercard | `5241 0198 2664 6950` | 123 | 11/30 |
| Débito | Visa | `4023 6535 2391 4373` | 123 | 11/30 |

### **Escenarios de Prueba según Titular**

Cambia el **nombre del titular** para simular diferentes resultados:

| Nombre Titular | Documento | Estado Esperado | Descripción |
|----------------|-----------|-----------------|-------------|
| `APRO` | 123456789 | PAGADO | ✅ Pago aprobado |
| `OTHE` | 123456789 | RECHAZADO | ❌ Rechazado por error general |
| `CONT` | 123456789 | PENDIENTE | ⏳ Pendiente de pago |
| `CALL` | 123456789 | RECHAZADO | 📞 Requiere autorización |
| `FUND` | 123456789 | RECHAZADO | 💰 Fondos insuficientes |
| `SECU` | 123456789 | RECHAZADO | 🔒 CVV inválido |
| `EXPI` | 123456789 | RECHAZADO | 📅 Fecha vencida |
| `FORM` | 123456789 | RECHAZADO | 📝 Error en formulario |

**Ejemplo de uso:**

```json
{
  "numero_tarjeta": "4168818844447115",
  "mes_vencimiento": 11,
  "anio_vencimiento": 2030,
  "cvv": "123",
  "nombre_titular": "APRO",  // ← Cambiar aquí para simular diferentes escenarios
  "email": "test@example.com",
  "descripcion": "Pago de prueba",
  "monto": 5000.0
}
```

---

## 📁 Estructura del Proyecto

```
proyecto-microservicios/
├── .env                          # ⚠️ Variables de entorno (AGREGAR TOKENS AQUÍ)
├── .gitignore                    # Archivos ignorados por Git
├── docker-compose.yml            # Configuración de Docker Compose
├── README.md                     # Este archivo
├── test_pago_tarjeta.py         # 🧪 Script de pruebas automáticas
│
└── app-pagos/                    # Servicio de pagos
    ├── Dockerfile                # Imagen Docker del servicio
    ├── requirements.txt          # Dependencias Python
    ├── .env.example              # Ejemplo de variables de entorno
    │
    └── app/
        ├── main.py               # Aplicación FastAPI principal
        ├── routers/
        │   ├── __init__.py
        │   └── pagos.py          # Endpoints de pagos
        └── schemas/
            ├── __init__.py
            └── pago.py           # Modelos Pydantic
```

---

## 🔍 Troubleshooting

### **Problema: El servicio no inicia**

```bash
# Verificar logs del contenedor
docker logs app-pagos

# Verificar que el puerto 8002 no esté ocupado
lsof -i :8002

# Reiniciar el servicio
docker-compose restart app-pagos
```

---

### **Problema: Error "MP_ACCESS_TOKEN no configurado"**

**Causa:** Las credenciales de MercadoPago no están configuradas.

**Solución:**

1. Edita el archivo `.env` en la raíz del proyecto
2. Agrega tus credenciales de prueba de MercadoPago
3. Reinicia el servicio:

```bash
docker-compose down
docker-compose up -d
```

---

### **Problema: Error "mercadopago_status: missing credentials"**

**Causa:** El contenedor no está leyendo las variables de entorno correctamente.

**Solución:**

```bash
# 1. Verificar que el archivo .env existe en la raíz
cat .env

# 2. Verificar que las variables están configuradas
docker exec app-pagos env | grep MP_

# 3. Si no aparecen, reconstruir el contenedor
docker-compose down
docker-compose up --build -d
```

---

### **Problema: Pago rechazado con tarjeta de prueba**

**Causa:** El nombre del titular no coincide con los escenarios de prueba.

**Solución:** Usa exactamente los nombres de titular especificados en la tabla de escenarios:
- `APRO` para pagos aprobados
- `FUND` para fondos insuficientes
- `OTHE` para error general
- etc.

---

### **Problema: "Connection refused" al ejecutar test_pago_tarjeta.py**

**Causa:** El servicio no está corriendo.

**Solución:**

```bash
# Verificar que el contenedor esté corriendo
docker ps | grep app-pagos

# Si no está corriendo, levantarlo
docker-compose up -d

# Esperar unos segundos y verificar salud
curl http://localhost:8002/health
```

---

## 🛡️ Seguridad

### **Buenas Prácticas**

- ✅ **Nunca** versiones el archivo `.env` con credenciales reales
- ✅ Usa credenciales de **PRUEBA** (TEST) para desarrollo
- ✅ Usa credenciales de **PRODUCCIÓN** solo en ambiente productivo
- ✅ Configura HTTPS en producción
- ✅ Implementa rate limiting para evitar abuso
- ✅ Valida todos los datos de entrada
- ✅ Registra logs de todas las transacciones

### **Variables de Entorno Sensibles**

El archivo `.gitignore` está configurado para **NO** versionar archivos `.env`. Asegúrate de:

1. Mantener tus credenciales seguras
2. No compartir tu `MP_ACCESS_TOKEN` públicamente
3. Rotar credenciales periódicamente
4. Usar variables de entorno en producción (no archivos .env)

---

## 📚 Documentación Adicional

- [Documentación oficial de MercadoPago](https://www.mercadopago.com.ar/developers/es/docs)
- [API Reference de MercadoPago](https://www.mercadopago.com.ar/developers/es/reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

---

## 📝 Notas Importantes

1. **Este servicio NO guarda información de pagos en base de datos**
   - Todos los datos se mantienen en memoria durante la ejecución
   - Al reiniciar el servicio, se pierden los registros de pagos
   - Para persistencia, integrar con una base de datos externa

2. **Timeout de pagos**
   - Los pagos pendientes expiran después de 120 segundos
   - Después de expirar, el estado cambia a `EXPIRADO`

3. **Webhooks**
   - Para recibir notificaciones de MercadoPago en producción
   - Configurar `MP_WEBHOOK_URL` con una URL pública accesible
   - MercadoPago enviará notificaciones POST a esta URL

---

## 🤝 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Troubleshooting](#-troubleshooting)
2. Verifica los logs del contenedor: `docker logs app-pagos`
3. Consulta la [documentación de MercadoPago](https://www.mercadopago.com.ar/developers/es/support)

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**¡Listo para procesar pagos! 🚀💳**
