#!/bin/sh
# start.sh — Nginx entrypoint for Railway and local docker-compose
#
# Railway:  copies nginx.railway.conf as a template to
#           /etc/nginx/templates/default.conf.template during the build.
#           At runtime we run envsubst to inject PORT / *_PORT variables
#           and write the final config before starting nginx.
#
# Local:    nginx.conf is copied directly to /etc/nginx/conf.d/default.conf
#           during the build — no variable substitution needed, just start nginx.

TEMPLATE=/etc/nginx/templates/default.conf.template
CONF=/etc/nginx/conf.d/default.conf

if [ -f "$TEMPLATE" ]; then
    echo "Railway environment detected — processing template with envsubst"
    envsubst '${PORT} ${FRONTEND_PORT} ${WEB_PORT} ${BACKEND_PORT}' \
        < "$TEMPLATE" > "$CONF"
else
    echo "Local environment detected — using nginx.conf directly"
fi

exec nginx -g "daemon off;"