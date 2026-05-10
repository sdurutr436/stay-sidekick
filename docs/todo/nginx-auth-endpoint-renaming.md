# Actualizar Nginx: endpoint auth_request renombrado

## Contexto

La ruta interna usada por Nginx para `auth_request` fue renombrada:

- **Antes:** `GET /api/auth/verify`
- **Después:** `GET /api/auth/validacion`

## Paso a seguir

En la configuración de Nginx (normalmente `nginx.conf` o el bloque `location` del proxy),
busca la directiva `auth_request` que apunta al endpoint anterior y actualiza la URL:

```nginx
# Antes:
auth_request /api/auth/verify;

# Después:
auth_request /api/auth/validacion;
```

Si usas Railway u otro servicio con Nginx gestionado, actualiza la variable de entorno
o el fichero de configuración correspondiente y redespliega.

## Verificación

Tras el cambio, comprueba que:

1. Las rutas protegidas siguen devolviendo 401 cuando el JWT es inválido.
2. Las rutas protegidas son accesibles con un JWT válido.
3. El endpoint `GET /api/auth/validacion` devuelve 200 con un JWT válido y 401 sin él.
