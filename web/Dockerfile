# =============================================================================
# WEB — 11ty (multi-stage)
# IMPORTANTE: el contexto de build debe ser la RAÍZ del proyecto, no web/
#   docker build -f web/Dockerfile .
# Esto es necesario porque sass compila desde frontend/src/styles/
# via --load-path=../frontend/src/styles (ver web/package.json).
# En docker-compose el contexto se define como context: .
# =============================================================================

# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

# Site key de Turnstile — pública, se incrusta en el HTML generado
ARG TURNSTILE_SITE_KEY
ENV TURNSTILE_SITE_KEY=$TURNSTILE_SITE_KEY

WORKDIR /app

# Instalar dependencias de 11ty primero (capa de caché independiente)
COPY web/package*.json ./web/
RUN cd web && npm ci

# Copiar los estilos SCSS de Angular — necesarios para sass --load-path
# Cuando sass ejecuta desde /app/web, busca ../frontend/src/styles → /app/frontend/src/styles
COPY frontend/src/styles/ ./frontend/src/styles/

# Copiar el resto del proyecto 11ty
COPY web/ ./web/

# Compilar CSS (sass) + sitio estático (eleventy)
RUN cd web && npm run build

# ── Stage 2: Serve ────────────────────────────────────────────────────────────
FROM nginx:alpine

COPY web/nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /app/web/_site /usr/share/nginx/html

ENV PORT=80
EXPOSE 80
