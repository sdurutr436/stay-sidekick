# Migraciones de base de datos — Flask-Migrate / Alembic

Referencia completa sobre cómo se gestiona el esquema de PostgreSQL en Stay Sidekick,
incluyendo el problema original que motivó este sistema y cómo operarlo en el día a día.

---

## Problema original (abril 2026)

### Síntoma

El contenedor del backend en Railway arrancaba correctamente pero cualquier ruta que
tocara la base de datos fallaba con un error tipo `UndefinedTable` o equivalente.
El healthcheck de Railway (`/api/health`) respondía `200 OK` porque no hace ninguna
query, enmascarando el fallo real. El panel de inicio de sesión era inutilizable.

### Causa raíz

El `app factory` (`backend/app/__init__.py`) inicializaba SQLAlchemy con `db.init_app(app)`
e importaba los modelos para registrarlos en el metadata de SQLAlchemy, pero **nunca
creaba las tablas en PostgreSQL**. Railway provisiona la base de datos vacía —
no ejecuta ningún SQL automáticamente — por lo que el esquema nunca existió.

### Por qué no se usó `db.create_all()`

`db.create_all()` crea las tablas que faltan en el arranque, lo que resuelve el
problema inmediato. Sin embargo, **solo crea tablas nuevas; no modifica columnas
existentes**. Si en el futuro se añade una columna a un modelo, la tabla en
producción seguiría teniendo el esquema antiguo y el código nuevo fallaría en
silencio o con errores de columna. Para un proyecto en desarrollo activo esto es
un riesgo real.

### Solución adoptada: Flask-Migrate (Alembic)

Se integró **Flask-Migrate**, que envuelve **Alembic** (el estándar de migraciones
para SQLAlchemy). En lugar de que la app cree las tablas al arrancar, Alembic
mantiene un historial versionado de scripts de migración en `backend/migrations/versions/`.

El Dockerfile ejecuta `flask db upgrade` antes de arrancar Gunicorn. Este comando:

1. Comprueba la tabla interna `alembic_version` en la BD.
2. Detecta qué migraciones están pendientes.
3. Las aplica en orden.
4. Si no hay nada nuevo, sale en < 1 segundo sin tocar la BD.

Es **idempotente**: seguro de ejecutar en cada despliegue.

---

## Archivos añadidos / modificados

| Fichero | Cambio |
|---------|--------|
| `backend/requirements.txt` | Se añadió `flask-migrate==4.1.0` |
| `backend/app/extensions.py` | Se añadió instancia `Migrate()` |
| `backend/app/__init__.py` | Se llamó a `migrate.init_app(app, db)` |
| `backend/Dockerfile` | `CMD` cambiado a `flask db upgrade && gunicorn ...` + `ENV FLASK_APP=run.py` |
| `backend/migrations/` | Carpeta de Alembic generada manualmente (sin BD local disponible) |
| `backend/migrations/versions/a1b2c3d4e5f6_initial.py` | Migración inicial con las 9 tablas del esquema |
| `backend/seed.sql` | Script SQL con empresa demo y dos usuarios administradores |

---

## Operativa diaria

### Aplicar migraciones pendientes (Railway / producción)

Ocurre automáticamente en cada despliegue gracias al `CMD` del Dockerfile.
Si necesitas forzarlo manualmente desde el shell de Railway:

```bash
flask db upgrade
```

### Crear una nueva migración tras modificar un modelo

```bash
# 1. Modifica el modelo en backend/app/models/
# 2. Genera el script de migración automáticamente
flask db migrate -m "descripción del cambio"

# 3. Revisa el fichero generado en migrations/versions/
#    Alembic puede no detectar algunos cambios (constraints, índices funcionales)
#    — siempre revisarlo a mano antes de commitear.

# 4. Aplica en local
flask db upgrade
```

### Revertir la última migración

```bash
flask db downgrade
```

### Ver el historial de migraciones

```bash
flask db history
flask db current   # versión actualmente aplicada en la BD
```

---

## Seed de datos — usuarios iniciales

El fichero `backend/seed.sql` crea una empresa demo y dos usuarios con rol `admin`
y acceso a todas las herramientas. Debe ejecutarse **después** de que las tablas
existan (es decir, después de `flask db upgrade`).

### Ejecutar en Railway

1. Ir a **Railway → proyecto → servicio PostgreSQL → Data → Query**.
2. Pegar el contenido de `backend/seed.sql` y ejecutar.

### Ejecutar en local con Docker

```bash
docker compose exec postgres psql -U postgres -d stay_sidekick \
  -c "$(cat backend/seed.sql)"
```

### Credenciales creadas

| Email | Contraseña | Rol |
|-------|-----------|-----|
| `duran.utrerasergio2612@gmail.com` | `ElFuturoPuedeCambiarse13` | admin |
| `admin@staysidekick.es` | `RafaelAlberti2026!` | admin |

> Los hashes están generados con bcrypt (12 rounds). El script es idempotente
> gracias a `ON CONFLICT DO NOTHING`.

---

## Troubleshooting

**`flask db upgrade` falla con `relation "alembic_version" does not exist`**
→ Normal en una BD completamente nueva. Alembic crea la tabla `alembic_version`
automáticamente en el primer `upgrade`. No es un error real — vuelve a ejecutar.

**`flask db migrate` no detecta mis cambios**
→ Alembic no detecta automáticamente todos los tipos de cambios (renombrados,
cambios de tipo con cast, índices funcionales, constraints CHECK). En esos casos,
editar el script generado a mano o escribirlo desde cero.

**La BD tiene tablas pero Alembic no lo sabe (`alembic_version` vacío)**
→ La BD fue creada con `db.create_all()` antes de migrar a Alembic. Marcar
la migración inicial como aplicada sin ejecutarla:
```bash
flask db stamp a1b2c3d4e5f6
```
Esto le dice a Alembic "este estado ya existe" sin tocar las tablas.
