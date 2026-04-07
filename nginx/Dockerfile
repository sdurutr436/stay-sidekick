FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf

# RAILWAY=true → nginx.railway.conf (red privada .railway.internal + resolver IPv6)
# RAILWAY=false (default) → nginx.conf (docker-compose, hostnames de servicio)
ARG RAILWAY=true
COPY nginx.conf nginx.railway.conf /tmp/
RUN mkdir -p /etc/nginx/templates && \
    if [ "$RAILWAY" = "true" ]; then \
      cp /tmp/nginx.railway.conf /etc/nginx/templates/default.conf.template; \
    else \
      cp /tmp/nginx.conf /etc/nginx/conf.d/default.conf; \
    fi

# Defaults para envsubst — Railway sobreescribe PORT; los puertos de upstream
# se configuran con reference variables: FRONTEND_PORT=${{frontend.PORT}}, etc.
ENV PORT=80
ENV FRONTEND_PORT=80
ENV WEB_PORT=80
ENV BACKEND_PORT=5000

EXPOSE 80
