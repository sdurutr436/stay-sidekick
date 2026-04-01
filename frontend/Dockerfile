# =============================================================================
# FRONTEND — Angular (multi-stage)
# Stage 1: compilación con Node
# Stage 2: servidor nginx con los archivos estáticos
#
# Angular se construye con --base-href=/app/ para que el proxy inverso
# lo sirva bajo el prefijo /app/ sin conflicto con el sitio 11ty en /.
# =============================================================================

# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar manifiestos primero para aprovechar la caché de capas
COPY package*.json ./
RUN npm ci

# Copiar el resto del código fuente
COPY . .

# Compilar en modo producción con base-href para el prefijo /app/
RUN npm run build -- --base-href=/app/

# ── Stage 2: Serve ────────────────────────────────────────────────────────────
FROM nginx:alpine

# Configuración nginx para SPA (Angular Router necesita try_files → index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar el build de Angular al directorio web de nginx
# Angular CLI >= 17 genera en dist/<nombre>/browser/
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
