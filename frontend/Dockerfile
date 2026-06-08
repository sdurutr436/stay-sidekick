# =============================================================================
# FRONTEND — Angular (multi-stage)
# Stage 1: compilación con Node
# Stage 2: servidor nginx con los archivos estáticos
#
# Angular se construye con --base-href=/menu/ para que el proxy inverso
# lo sirva bajo el prefijo /menu/ sin conflicto con el sitio 11ty en /.
#
# inlineCritical: false (angular.json → optimization.styles)
#   Por defecto, Angular (Beasties) carga el CSS global con:
#     <link rel="stylesheet" media="print" onload="this.media='all'">
#   El atributo onload es un inline event handler controlado por script-src.
#   La CSP estricta de nginx lo bloquea y el CSS nunca se aplica en pantalla.
#   Con inlineCritical: false se genera un <link rel="stylesheet"> directo,
#   compatible con la CSP sin necesidad de añadir 'unsafe-inline' a script-src.
#
# Gestor de paquetes: pnpm (activado vía corepack a partir del campo
# "packageManager" de package.json — versión reproducible en builds).
# =============================================================================

# ── Stage 1: Build ────────────────────────────────────────────────────────────
# node:20-slim (Debian) — sólo etapa de build, se descarta en el stage final
FROM node:20-alpine AS builder

WORKDIR /app

# Activar pnpm vía corepack (incluido en Node ≥ 16); usa la versión declarada
# en el campo "packageManager" de package.json para garantizar reproducibilidad.
RUN corepack enable

# Copiar manifiestos primero para aprovechar la caché de capas
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copiar el resto del código fuente
COPY . .

# Compilar en modo producción con base-href para el prefijo /app/
# pnpm exec invoca ng directamente: evita el doble `--` que pnpm 10 reenvía
# literalmente al script (`ng build -- --base-href`), rechazado por Angular CLI.
RUN pnpm exec ng build --base-href=/menu/

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
