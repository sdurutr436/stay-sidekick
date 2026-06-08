# 6. Desarrollo

## Indice

- [6.1. Secuencia de desarrollo](#61-secuencia-de-desarrollo)
- [6.2. Dificultades encontradas y como se abordaron](#62-dificultades-encontradas-y-como-se-abordaron)
- [6.3. Decisiones tecnicas clave y su justificacion](#63-decisiones-tecnicas-clave-y-su-justificacion)
- [6.4. Control de versiones](#64-control-de-versiones)
- [6.5. Fragmentos de codigo relevantes](#65-fragmentos-de-codigo-relevantes)

---

## 6.1. Secuencia de desarrollo

El desarrollo se siguio de forma incremental y por bloques funcionales, cerrando primero diseño y estructura, y despues cada herramienta del MVP.

### Fase 1 - diseño previo en Figma

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

## 6.2. Dificultades encontradas y como se abordaron

### Compartir estilos reales entre 11ty y Angular

El proyecto necesitaba una unica fuente de estilos para sitio publico y panel SPA. La compilacion del sitio 11ty dependia de `frontend/src/styles`, lo que obligo a construir `web` con contexto de build en la raiz en lugar de `web/`. Se resolvio ajustando Dockerfile y compose para soportar ese path compartido sin duplicar CSS.

### Bloqueo de CSS por CSP estricta en frontend

Durante el build de Angular, la carga diferida de CSS usando `onload` en `<link>` provocaba bloqueo con CSP estricta en Nginx. Ademas, en el sitio publico aparecieron bloqueos de scripts inline usados para evitar FOUC. Se soluciono desactivando inline critical CSS en la configuracion de estilos y externalizando los scripts iniciales a ficheros JS dedicados, de forma compatible con la politica de seguridad.

### Correcciones iterativas de accesibilidad y consistencia visual

Las auditorias de accesibilidad y la validacion manual detectaron problemas no funcionales pero relevantes para calidad de producto: botones sin nombre accesible, `aria-label` vacios, atributos ARIA redundantes y contrastes mejorables en algunos estados. Estas incidencias no se resolvieron en un unico cambio, sino en varias tandas de fixes sobre web y frontend, afinando componentes, navegacion y modo visual hasta dejar una base mas consistente.

### Despliegue en Railway con Nginx y rutas inconsistentes

En despliegue aparecieron errores 502 y navegacion inestable por varias causas acumuladas: arranque incompleto del contenedor Nginx en Railway, rutas sin barra final en la configuracion del proxy y una escucha incorrecta del servicio publico en el puerto `8080` cuando debia exponerse en el `80`. Se introdujo un `start.sh` especifico para Nginx en Railway, se unificaron las rutas con trailing slash para reducir redirecciones innecesarias y se corrigio la escucha al puerto `80`. Con ese ajuste, el acceso publico a `stay-sidekick.com` quedo estabilizado y el 502 asociado al dominio se dio por resuelto.

### Restricciones SMTP del entorno gestionado y migracion a Mailgun

El envio de correos transaccionales encontro limitaciones del proveedor de despliegue: Railway bloqueaba el puerto 587 en ciertos escenarios, lo que impedia usar la configuracion SMTP esperada con Gmail. Se anadio soporte SSL/TLS alternativo en el servicio de correo y se probaron ajustes de configuracion para adaptarse al entorno, pero el envio SMTP en produccion no quedo resuelto de forma estable.

La solucion definitiva fue abandonar SMTP y migrar a **Mailgun via HTTP API con API key**. El servicio de correo ahora hace un `POST` autenticado contra `https://api.eu.mailgun.net/v3/<MAIL_GUN_DOMAIN>/messages` (o la region US segun `MAIL_GUN_API_URL`) usando `MAIL_GUN_API_KEY` como credencial, lo que elimina por completo la dependencia de puertos SMTP salientes y la app password de Gmail. La configuracion se reduce a tres variables (`MAIL_GUN_API_KEY`, `MAIL_GUN_DOMAIN`, `MAIL_GUN_API_URL`) mas `MAIL_FROM`, y el modulo de envio paso de `smtplib` a `requests`.

### Convivencia JWT + CSRF en SPA

Aunque JWT protege autenticacion, los endpoints de escritura requerian proteccion adicional frente a CSRF. Se implemento patron double-submit cookie (`csrf_token` en cookie + header `X-CSRF-Token`) para mantener un flujo stateless seguro en frontend y backend. Mas adelante se endurecio la configuracion de cookies para entornos seguros, evitando que la proteccion quedara debilitada en despliegue.

### Variabilidad de entradas PMS/XLSX

Las fuentes externas no siempre entregan campos homogeneos (cabeceras, formatos, columnas opcionales). Se incorporaron validaciones y capa de normalizacion por modulo para convertir todas las entradas al mismo contrato interno antes de persistir o procesar.

### OAuth de Google en distintos entornos

El callback OAuth y los redirects de frontend variaban entre local y despliegue. Ademas, el flujo exigio reforzar la gestion de `state` para evitar retornos invalidos o reutilizacion indebida. Se centralizo con `FRONTEND_BASE_URL` y verificacion firmada con caducidad del `state` para evitar errores de retorno y reforzar seguridad del flujo OAuth.

### Errores 500 por tipado heterogeneo en sincronizacion

La integracion con proveedores externos genero fallos de ejecucion al procesar campos de fecha con tipos distintos segun el origen. En un fix del sincronizador se detecto el caso de cadenas tratadas como si fueran objetos fecha, provocando errores 500. Se corrigio endureciendo la normalizacion y el tratamiento defensivo de tipos antes de transformar o serializar datos.

### Migraciones no idempotentes en base de datos

Durante la evolucion del modulo de mapa de calor aparecieron fallos en migraciones cuando una constraint ya habia sido eliminada o creada en una ejecucion previa. Esto rompia despliegues repetibles y entornos de integracion. Se resolvio haciendo las operaciones de alteracion de esquema idempotentes, con comprobaciones previas antes de eliminar o recrear restricciones.

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

El proyecto usa Git con repositorio en GitHub y una estrategia de ramas por trabajo tematico e integracion progresiva.

Patron aplicado durante el desarrollo:

- Ramas de trabajo por objetivo (`dev-*`, `feat-*`, `fix-*`).
- Integracion frecuente en `dev-herramientas` como rama de consolidacion tecnica.
- Promocion posterior a `main` mediante merges documentados tras validar CI y estabilidad.

Esta estructura permitio aislar experimentacion funcional, agrupar fixes relacionados y retrasar la promocion a `main` hasta tener una version mas estable del conjunto.

Evidencias verificables del flujo en historial:

- `bb85b3c`: `merge: fix-accesibilidad-auditoria -> dev-herramientas`, incorporando correcciones WCAG, mejoras de la web estatica y cobertura frontend reforzada.
- `ddefdd7`: `merge: dev-mail-service -> dev-herramientas`, integrando un servicio de correo reutilizable antes de consolidarlo en ramas superiores.
- `9973356`: `merge: dev-herramientas -> main`, llevando a principal la refactorizacion API REST, ajustes de roles y mejoras de notificaciones y Swagger.
- `28afe36`: `merge: dev-herramientas -> main`, consolidando cambios de DevOps, headers Nginx, endurecimiento de contenedores y CI con PostgreSQL.
- `b87a427`: `merge: dev-herramientas -> main`, agrupando ajustes de `start.sh` para Railway y pruebas de soporte SSL para SMTP (sustituido despues por la migracion a Mailgun HTTP API).
- `88daebb`: `merge: dev-herramientas -> main`, incorporando fixes de rutas Nginx y nuevas correcciones de accesibilidad.

Automatizacion de versionado y calidad:

- `CI Python`: lint con ruff + tests con PostgreSQL de servicio.
- `CI Angular`: build del frontend.
- `CI 11ty`: build del sitio estatico.
- `Docker Hub`: publica imagenes solo cuando los tres CI del mismo SHA han pasado.

---

## 6.5. Fragmentos de codigo relevantes

Los siguientes fragmentos se seleccionaron comprobando su presencia en las ramas activas `main` y `dev-herramientas`.
El envio SMTP que en su dia quedo pendiente se reemplazo por la integracion con Mailgun (HTTP + API key), por lo que esa parte ya forma parte del comportamiento consolidado y no se excluye de la seleccion.

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
RUN pnpm run build -- --base-href=/menu/
```

El frontend se sirve bajo `/menu` detras de Nginx. Este ajuste evita rutas rotas al desplegar y fue clave para convivir con el sitio 11ty servido en `/`.

### 7) OAuth Google con `state` firmado y caducidad

Archivo: `backend/app/h_sincronizador_contactos/service.py`

```python
def _oauth_serializer():
    from itsdangerous import URLSafeTimedSerializer
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="google-oauth")


def build_oauth_url(empresa_id: str) -> str:
    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    state = _oauth_serializer().dumps({"e": empresa_id, "n": secrets.token_urlsafe(8)})
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": _SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    query = urlencode(params)
    return f"{_GOOGLE_AUTH_URL}?{query}"


_OAUTH_STATE_TTL = 600  # 10 minutos


def verify_oauth_state(state: str) -> str | None:
    from itsdangerous import BadSignature, SignatureExpired
    try:
        data = _oauth_serializer().loads(state, max_age=_OAUTH_STATE_TTL)
        return data.get("e")
    except (BadSignature, SignatureExpired):
        return None
```

Este fragmento refleja como se reforzo el flujo OAuth mas alla del redireccionamiento basico: el `state` no solo viaja en la URL, sino que va firmado y con caducidad, reduciendo riesgo de retorno invalido o reutilizacion indebida.

### 8) Parseo XLSX configurable y tolerante a cabeceras

Archivo: `backend/app/h_sincronizador_contactos/service.py`

```python
cols = prefs.get("xlsx_reservas") or {}
col_checkin   = int(cols.get("col_checkin", 0))
col_nombre    = int(cols.get("col_nombre", 0))
col_tipologia = int(cols.get("col_tipologia", 0))
col_telefono  = int(cols.get("col_telefono", 0))

_HEADER_MAP = {
    "checkin": ["checkin", "check-in", "check_in", "fecha_entrada", "arrival", "entrada"],
    "nombre": ["nombre", "name", "guest", "huesped", "huésped", "guest_name", "referencia"],
    "tipologia": ["tipologia", "tipología", "id_tipologia", "unit_type", "tipo"],
    "telefono": ["telefono", "teléfono", "phone", "tel", "movil", "móvil"],
}

def _find_col(configured: int, candidates: list[str]) -> int | None:
    if configured > 0:
        return configured - 1
    for i, h in enumerate(headers):
        if h in candidates:
            return i
    return None

idx_nombre = _find_col(col_nombre, _HEADER_MAP["nombre"])
if idx_nombre is None:
    return [], [
        "No se encontró columna de nombre del huésped. "
        "Configura la posición de columna en el perfil o añade una cabecera reconocida."
    ]
```

Resume bien la capa de normalizacion que hizo viable el fallback XLSX: cada empresa puede fijar columnas manualmente, pero el sistema tambien intenta reconocer cabeceras equivalentes para soportar archivos heterogeneos sin romper el flujo.

### 9) Migracion idempotente para evitar despliegues fragiles

Archivo: `backend/migrations/versions/f6a7b8c9d0e1_add_heatmap_pms_origen.py`

```python
def upgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'logs_sincronizacion_origen_check'
                AND conrelid = 'logs_sincronizacion'::regclass
            ) THEN
                ALTER TABLE logs_sincronizacion DROP CONSTRAINT logs_sincronizacion_origen_check;
            END IF;
        END $$;
    """)
    op.create_check_constraint(
        "logs_sincronizacion_origen_check",
        "logs_sincronizacion",
        "origen IN ('pms', 'google_contacts', 'xlsx', 'heatmap_pms')",
    )
```

Este cambio es representativo de un problema menos visible pero importante: las migraciones no siempre fallan por SQL incorrecto, sino por asumir un estado previo que puede no cumplirse. La comprobacion previa hace el despliegue mucho mas repetible.

### 10) Contrato OpenAPI de autenticacion y CSRF

Archivo: `backend/app/docs/openapi.yaml`

```yaml
info:
  description: |
    ## Autenticación
    La mayoría de endpoints requieren un JWT en la cabecera `Authorization: Bearer <token>`.
    El token se obtiene en `POST /api/auth/login`.

    Los endpoints de escritura también exigen el **CSRF Double-Submit Cookie**:
    obten el token en `GET /api/csrf-token` y envíalo en la cabecera `X-CSRF-Token`.

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    CsrfToken:
      type: apiKey
      in: header
      name: X-CSRF-Token
```

Este fragmento muestra que la seguridad no se quedo en implementacion interna: el contrato de API documenta de forma explicita como deben autenticarse los clientes y que requisitos extra tienen las operaciones de escritura.
