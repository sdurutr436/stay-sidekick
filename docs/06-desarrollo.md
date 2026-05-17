# 6. Desarrollo

## Indice

- [6.1. Secuencia de desarrollo](#61-secuencia-de-desarrollo)
- [6.2. Dificultades encontradas y como se superaron](#62-dificultades-encontradas-y-como-se-superaron)
- [6.3. Decisiones tecnicas clave y su justificacion](#63-decisiones-tecnicas-clave-y-su-justificacion)
- [6.4. Control de versiones](#64-control-de-versiones)
- [6.5. Fragmentos de codigo relevantes](#65-fragmentos-de-codigo-relevantes)

---

## 6.1. Secuencia de desarrollo

El desarrollo se siguio de forma incremental y por bloques funcionales, cerrando primero diseno y estructura, y despues cada herramienta del MVP.

### Fase 1 - Diseno previo en Figma

Se definieron wireframes y flujo visual antes de implementar codigo, con el objetivo de reducir iteraciones de interfaz durante desarrollo. El recurso base de disenio se mantuvo en Figma como referencia unica para maquetacion y validacion.

### Fase 2 - Base del proyecto y arquitectura por capas

Se construyo la estructura monorepo con tres capas diferenciadas:

- `web/` (11ty + Nunjucks) para landing y contenido publico.
- `frontend/` (Angular) para el panel de herramientas.
- `backend/` (Flask) para API y logica de negocio.

En paralelo se definieron Dockerfiles por servicio y compose para ejecucion integrada local.

### Fase 3 - Sistema de estilos compartido y navegacion

Se consolido una arquitectura SCSS compartida (ITCSS + BEM) para mantener consistencia visual entre 11ty y Angular. Se implementaron layout, componentes base y navegacion por rutas del panel.

### Fase 4 - Seguridad y autenticacion

Se implemento el acceso al panel con JWT y proteccion CSRF tipo double-submit cookie, junto a rate limiting en endpoints sensibles. En esta fase tambien se establecio el modelo de autorizacion por rol (`operativo`, `admin`, `superadmin`).

### Fase 5 - Nucleo funcional multiempresa

Se construyo el modelo de datos multi-tenant (`empresa_id`) y el modulo de maestro de apartamentos:

- CRUD de apartamentos.
- Sincronizacion con PMS (Smoobu en MVP).
- Importacion XLSX con preview y normalizacion.

### Fase 6 - Herramientas operativas del MVP

Se implementaron progresivamente los modulos principales:

- Mapa de calor (PMS y XLSX).
- Notificaciones de check-in tardio.
- Sincronizador de contactos con Google OAuth + People API.
- Vault de comunicaciones con mejora/traduccion asistida por IA.
- Perfil e integraciones (PMS/IA, columnas XLSX y configuraciones de herramienta).

### Fase 7 - Hardening, documentacion y despliegue

Se reforzo la plataforma con:

- Cifrado de credenciales con Fernet.
- Configuracion de CSP y ajuste de build frontend para compatibilidad.
- Mejoras de contenedores (usuario no root en backend, separacion de red interna).
- CI por stack (Python, Angular, 11ty) y publicacion de imagenes en Docker Hub condicionada a CI exitoso.
- Documentacion tecnica y funcional por modulos.

---

## 6.2. Dificultades encontradas y como se superaron

### Compartir estilos reales entre 11ty y Angular

El proyecto necesitaba una unica fuente de estilos para sitio publico y panel SPA. La compilacion del sitio 11ty dependia de `frontend/src/styles`, lo que obligo a construir `web` con contexto de build en la raiz en lugar de `web/`. Se resolvio ajustando Dockerfile y compose para soportar ese path compartido sin duplicar CSS.

### Bloqueo de CSS por CSP estricta en frontend

Durante el build de Angular, la carga diferida de CSS usando `onload` en `<link>` provocaba bloqueo con CSP estricta en Nginx. Se soluciono desactivando inline critical CSS en la configuracion de estilos para generar enlaces compatibles con la politica de seguridad.

### Convivencia JWT + CSRF en SPA

Aunque JWT protege autenticacion, los endpoints de escritura requerian proteccion adicional frente a CSRF. Se implemento patron double-submit cookie (`csrf_token` en cookie + header `X-CSRF-Token`) para mantener un flujo stateless seguro en frontend y backend.

### Variabilidad de entradas PMS/XLSX

Las fuentes externas no siempre entregan campos homogeneos (cabeceras, formatos, columnas opcionales). Se incorporaron validaciones y capa de normalizacion por modulo para convertir todas las entradas al mismo contrato interno antes de persistir o procesar.

### OAuth de Google en distintos entornos

El callback OAuth y los redirects de frontend variaban entre local y despliegue. Se centralizo con `FRONTEND_BASE_URL` y verificacion firmada de `state` para evitar errores de retorno y reforzar seguridad del flujo OAuth.

### Gestion segura de claves de proveedores

El sistema maneja claves sensibles (PMS, IA, tokens Google). Para evitar persistir secretos en claro, se adopto cifrado simetrico Fernet en base de datos y solo se descifra en tiempo de uso.

---

## 6.3. Decisiones tecnicas clave y su justificacion

### Backend modular con Flask Blueprints

Se eligio una organizacion por modulos funcionales (`auth`, `perfil`, `apartamentos`, `contactos`, `vault`, etc.) para desacoplar dominios y facilitar mantenimiento incremental.

### Multi-tenant por `empresa_id`

El aislamiento por empresa se implemento en modelo de datos y servicios para garantizar separacion logica de informacion y configuracion por cliente.

### Fallback operativo API -> XLSX

No todas las empresas cuentan con API de PMS estable o disponible. Por ello cada herramienta critica incorpora camino alternativo por XLSX, permitiendo operar incluso sin integracion directa.

### Cifrado de secretos en BD

Las claves externas se almacenan cifradas con Fernet (`FERNET_KEY`) para reducir impacto ante lectura indebida de la base de datos.

### Seguridad por capas (JWT + CSRF + rate limit + CORS)

Se combinaron controles complementarios en lugar de un unico mecanismo: autenticacion JWT, CSRF para escrituras, limitacion de peticiones y origenes permitidos configurables.

### CI separado por tecnologia y publicacion condicionada

Se definieron pipelines independientes para Python, Angular y 11ty. La publicacion de imagenes Docker se habilita solo si los tres CI para el mismo commit estan en estado `success`.

---

## 6.4. Control de versiones

El proyecto usa Git con repositorio en GitHub y una estrategia de ramas por trabajo tematico.

Patron aplicado durante el desarrollo:

- Ramas de trabajo por objetivo (`dev-*`, `feat-*`, `fix-*`).
- Integracion mediante merges documentados en ramas de consolidacion.
- Promocion a rama principal tras validar CI y estabilidad.

Evidencias del flujo en historial:

- Merges de ramas de mejoras UI/UX y DevOps hacia ramas de integracion.
- Commits de hardening de Docker, CSP, variables de entorno y documentacion.
- Ramas especificas para Swagger/OpenAPI y mejoras de notificaciones.

Automatizacion de versionado y calidad:

- `CI Python`: lint con ruff + tests con PostgreSQL de servicio.
- `CI Angular`: build del frontend.
- `CI 11ty`: build del sitio estatico.
- `Docker Hub`: publica imagenes solo cuando los tres CI del mismo SHA han pasado.

---

## 6.5. Fragmentos de codigo relevantes

### 1) Login protegido con CSRF y rate limit

Archivo: `backend/app/auth/routes.py`

```python
@auth_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("10/hour")
@csrf_protect
def login():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    clean_data, errors = sanitize_login_payload(json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    token, errors, debe_cambiar = authenticate_user(clean_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 401

    return jsonify({"ok": True, "token": token, "debe_cambiar_password": debe_cambiar}), 200
```

Este fragmento resume la estrategia de acceso: limitar intentos, validar CSRF, sanitizar payload y emitir JWT solo tras credenciales correctas.

### 2) Implementacion de CSRF stateless (double-submit)

Archivo: `backend/app/security/csrf.py`

```python
def csrf_protect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie_token = request.cookies.get(_COOKIE_NAME)
        header_token = request.headers.get(_HEADER_NAME)

        if not cookie_token or not header_token:
            return jsonify({"ok": False, "errors": ["Token CSRF ausente."]}), 403

        if not secrets.compare_digest(cookie_token, header_token):
            return jsonify({"ok": False, "errors": ["Token CSRF invalido."]}), 403

        return f(*args, **kwargs)
    return decorated
```

Se evita mantener sesion de servidor: el backend solo compara cookie y cabecera, manteniendo un enfoque stateless compatible con API JWT.

### 3) Cifrado de API keys con Fernet

Archivo: `backend/app/common/crypto.py`

```python
def encrypt(plaintext: str) -> str:
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str | None:
    f = _get_fernet()
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        logger.error("Token Fernet invalido - posible clave incorrecta o dato corrupto")
        return None
```

Este bloque protege secretos de PMS/IA/Google en persistencia. La aplicacion nunca guarda claves en texto plano en tablas de configuracion.

### 4) Inyeccion automatica del JWT en Angular

Archivo: `frontend/src/app/interceptors/auth.interceptor.ts`

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();

  if (token && req.url.includes('/api/')) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }

  return next(req);
};
```

Evita repetir logica de autenticacion en cada servicio HTTP del frontend y garantiza consistencia del header `Authorization`.

### 5) Publicacion Docker condicionada a CI completo

Archivo: `.github/workflows/docker-publish.yml`

```yaml
on:
  workflow_run:
    workflows: [CI Angular, CI 11ty, CI Python]
    types: [completed]
    branches: [main]

jobs:
  verificar:
    outputs:
      todos-pasaron: ${{ steps.check.outputs.todos-pasaron }}

  publicar:
    needs: verificar
    if: needs.verificar.outputs.todos-pasaron == 'true'
```

Esta configuracion evita publicar imagenes si algun stack no ha pasado validacion en el mismo commit.

### 6) Ajuste de build Angular para prefijo y CSP

Archivo: `frontend/Dockerfile`

```dockerfile
# Compilar en modo producción con base-href para el prefijo /menu/
RUN npm run build -- --base-href=/menu/
```

El frontend se sirve bajo `/menu` detras de Nginx. Este ajuste evita rutas rotas al desplegar y fue clave para convivir con el sitio 11ty servido en `/`.
