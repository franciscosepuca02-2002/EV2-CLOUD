#!/bin/sh
# Reescribe /usr/share/nginx/html/assets/config.json con la API_URL del entorno
# para que el mismo build sirva en local, AWS, etc.

API_URL="${API_URL:-http://localhost:8000}"

cat > /usr/share/nginx/html/assets/config.json <<EOF
{
  "apiUrl": "${API_URL}"
}
EOF

echo "[entrypoint] config.json escrito con apiUrl=${API_URL}"
