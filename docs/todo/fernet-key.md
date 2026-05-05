# Configurar FERNET_KEY

La clave Fernet cifra las API keys (PMS, IA) antes de guardarlas en la BD.
Sin ella, guardar cualquier API key devuelve 422.

## 1. Generar la clave (una sola vez)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Guarda el resultado — es algo como `abc123...==`. **No lo pierdas ni lo compartas.**

## 2. Añadirla al entorno local

En `backend/.env`:

```
FERNET_KEY=<clave generada>
```

## 3. Añadirla en Railway

Variables → New variable → `FERNET_KEY` = `<clave generada>`

**Usa la misma clave en local y en Railway.** Si cambias la clave, las API keys
ya cifradas en BD quedarán ilegibles y habrá que reconfigurarlas.
