# Stage 1: build Angular
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration production

# Stage 2: nginx servir el dist
FROM nginx:alpine

# Borrar config default
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nginx.conf custom
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar build (Angular 17+ usa "browser" subfolder)
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

# Script para reemplazar API_URL en config.json al arrancar (runtime config)
COPY entrypoint.sh /docker-entrypoint.d/40-config.sh
RUN chmod +x /docker-entrypoint.d/40-config.sh

EXPOSE 80

# nginx ya tiene CMD por defecto
