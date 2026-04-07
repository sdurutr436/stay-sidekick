# =============================================================================
# BACKEND — Flask
# Imagen ligera Python. run.py ya arranca con host=0.0.0.0.
# Para producción real sustituir `python run.py` por gunicorn.
# =============================================================================

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero para caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

EXPOSE 5000

# Gunicorn con dual-stack IPv4+IPv6 — necesario para la red privada de Railway
CMD ["gunicorn", "--bind", "[::]:5000", "--workers", "2", "run:app"]
