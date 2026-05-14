# =============================================================================
# BACKEND — Flask
# Imagen ligera Python. run.py ya arranca con host=0.0.0.0.
# Para producción real sustituir `python run.py` por gunicorn.
# =============================================================================

FROM python:3.11-slim

# Evitar buffering para que los logs aparezcan inmediatamente en Railway
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero para caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Ejecutar como usuario no root (seguridad)
RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app
USER app

EXPOSE 5000

# FLASK_APP necesario para que `flask db upgrade` encuentre la app
ENV FLASK_APP=run.py

# 1. Aplica las migraciones pendientes (idempotente — seguro en cada arranque)
# 2. Arranca Gunicorn con dual-stack IPv4+IPv6 (necesario en la red privada de Railway)
# Shell form para expandir $PORT (inyectado por Railway; fallback a 5000)
CMD flask db upgrade && gunicorn --bind "[::]:${PORT:-5000}" --workers 2 run:app
