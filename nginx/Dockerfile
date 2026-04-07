FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf

# RAILWAY=true → nginx.railway.conf (red privada .railway.internal + resolver IPv6)
# RAILWAY=false (default) → nginx.conf (docker-compose, hostnames de servicio)
ARG RAILWAY=true
COPY nginx.conf nginx.railway.conf /tmp/
RUN if [ "$RAILWAY" = "true" ]; then \
      cp /tmp/nginx.railway.conf /etc/nginx/conf.d/default.conf; \
    else \
      cp /tmp/nginx.conf /etc/nginx/conf.d/default.conf; \
    fi

EXPOSE 80
