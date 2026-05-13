# =============================================================================
# FRONTEND — Angular (multi-stage)
# Stage 1: compilación con Node
# Stage 2: servidor nginx con los archivos estáticos
#
# Angular se construye con --base-href=/app/ para que el proxy inverso
# lo sirva bajo el prefijo /app/ sin conflicto con el sitio 11ty en /.
# =============================================================================

# ── Stage 1: Build ────────────────────────────────────────────────────────────
# node:20-slim (Debian) — sólo etapa de build, se descarta en el stage final
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar manifiestos primero para aprovechar la caché de capas
COPY package*.json ./
RUN npm ci

# Copiar el resto del código fuente
COPY . .

# Compilar en modo producción con base-href para el prefijo /app/
RUN npm run build -- --base-href=/menu/

# ── Stage 2: Serve ────────────────────────────────────────────────────────────
# nginx:alpine — imagen final (Alpine minimiza la superficie de ataque; rebuild periódico para parches)
FROM nginx:alpine

# Configuración nginx para SPA (Angular Router necesita try_files → index.html)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copiar el build de Angular al directorio web de nginx
# Angular CLI >= 17 genera en dist/<nombre>/browser/
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

ENV PORT=80
EXPOSE 80
# USER nginx no se aplica: el proceso maestro de nginx necesita root para
# enlazar el puerto 80 (< 1024). Los worker processes ya corren como nginx
# por la directiva `user nginx` del nginx.conf interno.
