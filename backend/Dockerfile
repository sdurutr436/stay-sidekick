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

EXPOSE 5000

# Gunicorn con dual-stack IPv4+IPv6 — necesario para la red privada de Railway
# Shell form para expandir $PORT (inyectado por Railway; fallback a 5000)
CMD gunicorn --bind "[::]:${PORT:-5000}" --workers 2 run:app
