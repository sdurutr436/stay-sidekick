#!/bin/sh
# =============================================================================
# start.sh — Startup script for nginx reverse proxy on Railway
#
# Runs envsubst with an explicit list of variables so that only the four
# known port variables are substituted.  All other nginx variables
# ($remote_addr, $host, $scheme, …) are left untouched.
#
# Railway resolves reference variables (e.g. ${{frontend-sidekick.PORT}})
# into real environment variable values before the container starts, so
# FRONTEND_PORT, WEB_PORT, and BACKEND_PORT will already be real port
# numbers by the time this script runs.
# =============================================================================

set -e

# Substitute only the four port variables; leave every other $-expression alone.
envsubst '${PORT} ${FRONTEND_PORT} ${WEB_PORT} ${BACKEND_PORT}' \
    < /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

echo "Generated /etc/nginx/conf.d/default.conf:"
cat /etc/nginx/conf.d/default.conf

# Hand off to nginx in the foreground (PID 1).
exec nginx -g "daemon off;"
