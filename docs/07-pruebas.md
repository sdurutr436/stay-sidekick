# 7. Pruebas

## Índice

- [7.1. Metodología de pruebas](#71-metodología-de-pruebas)
- [7.2. Tipos de pruebas realizadas](#72-tipos-de-pruebas-realizadas)
  - [7.2.1. Pruebas de integración — Backend](#721-pruebas-de-integración--backend)
  - [7.2.2. Pruebas unitarias de servicio — Backend](#722-pruebas-unitarias-de-servicio--backend)
  - [7.2.3. Pruebas unitarias — Frontend](#723-pruebas-unitarias--frontend)
  - [7.2.4. Pruebas manuales de smoke y validaciones complementarias](#724-pruebas-manuales-de-smoke-y-validaciones-complementarias)
- [7.3. Cobertura de código](#73-cobertura-de-código)
  - [7.3.1. Frontend — Istanbul / Vitest](#731-frontend--istanbul--vitest)
  - [7.3.2. Backend — cobertura manual](#732-backend--cobertura-manual)
- [7.4. Resultados y estadísticas](#74-resultados-y-estadísticas)
  - [7.4.1. Desglose por suite — Backend](#741-desglose-por-suite--backend)
  - [7.4.2. Desglose por spec — Frontend](#742-desglose-por-spec--frontend)
  - [7.4.3. Integración continua](#743-integración-continua)

---

## 7.1. Metodología de pruebas

La estrategia de pruebas adoptada en Stay Sidekick combina diferentes enfoques según la capa
de la aplicación y el grado de criticidad de cada módulo. Este capítulo toma como referencia el
estado consolidado del proyecto en `main`, donde se reúne la batería de pruebas y workflows más completa del repositorio.

**Desarrollo guiado por contratos de comportamiento**  
Para las capas de seguridad — validación CSRF, verificación JWT y control de acceso por rol —
se definieron los comportamientos esperados antes de implementar la lógica definitiva, siguiendo
el espíritu del ciclo TDD. Por ejemplo, el test `test_login_sin_csrf_devuelve_403` fijó el
contrato de que cualquier petición al endpoint de login sin token CSRF sea rechazada con HTTP 403
antes de alcanzar la capa de credenciales, lo que permitió que el decorador `@csrf_protect`
quedara correctamente posicionado en la cadena de decoradores del blueprint de autenticación.

**Desarrollo paralelo para módulos funcionales**  
El resto de los módulos (apartamentos, vault, heatmap, contactos, perfil, usuarios, empresas) se
cubrieron con tests escritos en paralelo a la implementación: a medida que se creaba cada ruta se
definían los casos de prueba para los códigos HTTP esperados — 200, 201, 400, 401, 403, 404, 422
— verificando tanto el camino exitoso como los principales caminos de error.

**Pruebas manuales exploratorias**  
Los flujos que implican servicios externos — sincronización con la API de Smoobu, autorización
OAuth 2.0 de Google, mejora e traducción con proveedores de IA — se verificaron manualmente en
el entorno Docker local. Estos escenarios son difíciles de automatizar de forma fiable sin
infraestructura de sandbox dedicada y se documentaron como criterios de aceptación informales
durante el desarrollo.

La validación manual sobre el despliegue gestionado en Railway sigue siendo parcial dentro de los
resultados de este capítulo. El acceso público a `stay-sidekick.com` quedó restablecido al
corregir la escucha del servicio al puerto `80` en lugar de `8080`. El antiguo problema del envío
SMTP en producción se resolvió migrando el servicio de correo a **Mailgun por HTTP con API key**,
lo que elimina la dependencia de los puertos SMTP bloqueados por Railway. Las comprobaciones
consolidadas combinan entorno Docker local, suite automatizada de CI y verificaciones puntuales
en el entorno publicado.

**Pruebas de regresión automatizadas vía CI**  
La suite completa de pruebas automatizadas se ejecuta en cada *push* y *pull request* mediante
GitHub Actions, lo que garantiza que ningún cambio rompa comportamientos ya validados. El pipeline
de Python ejecuta también un paso previo de análisis estático con `ruff` para garantizar la
uniformidad del código antes de lanzar los tests.

---

## 7.2. Tipos de pruebas realizadas

### 7.2.1. Pruebas de integración — Backend

Las pruebas del backend utilizan **pytest** como ejecutor e instancian cada blueprint de Flask
de forma aislada, sin levantar la aplicación completa. Cada módulo de prueba sigue el mismo
patrón:

1. Se crea una aplicación Flask mínima que registra únicamente el blueprint bajo prueba.
2. Se genera un JWT de prueba firmado con el mismo algoritmo HS256 que usa la aplicación real.
3. Las dependencias externas (base de datos, servicios de PMS, proveedores de IA) se sustituyen
   con `unittest.mock.patch` para que los tests sean rápidos, deterministas y no requieran
   infraestructura real.
4. Se lanzan las peticiones HTTP con el `test_client` de Flask y se verifican el código de estado
   y el cuerpo JSON.

Aunque el cliente de tests de Flask no levanta un servidor TCP real, ejerce la totalidad del ciclo
de vida de la petición: routing, decoradores (CSRF, JWT, rate limit, roles), serialización de la
respuesta y manejo de errores. Por eso se clasifican como pruebas de **integración de capa HTTP**,
no como pruebas unitarias puras.

El siguiente fragmento del módulo `tests/auth/test_routes_auth.py` ilustra el patrón:

```python
@pytest.fixture
def client():
    """Instancia Flask mínima con únicamente el blueprint de autenticación."""
    from app.auth.routes import auth_bp
    from app.extensions import limiter

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(auth_bp)
    return app.test_client()


def test_login_sin_csrf_devuelve_403(client):
    """Sin token CSRF la petición es rechazada antes de procesar el JSON."""
    resp = client.post("/api/auth/login", json={"email": "a@a.com", "password": "x"})
    assert resp.status_code == 403


def test_login_exitoso_devuelve_token(client):
    csrf_headers = _set_csrf(client)
    with patch("app.auth.routes.authenticate_user", return_value=("jwt-fake", [], False)), \
         patch("app.auth.routes.sanitize_login_payload",
               return_value=({"email": "a@a.com", "password": "ok"}, [])):
        resp = client.post(
            "/api/auth/login",
            json={"email": "a@a.com", "password": "ok"},
            headers=csrf_headers,
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "token" in data
```

Otro ejemplo representativo es el test que verifica el control de acceso por rol en el módulo
de usuarios: un `operativo` recibe HTTP 403 donde un `admin` recibe HTTP 200:

```python
def test_list_usuarios_operativo_devuelve_403(client):
    resp = client.get("/api/usuarios", headers=_auth("operativo"))
    assert resp.status_code == 403


def test_list_usuarios_admin_devuelve_200(client):
    with patch("app.usuarios.routes.service.listar_usuarios",
               return_value={"usuarios": [], "max_usuarios": 4}):
        resp = client.get("/api/usuarios", headers=_auth("admin"))
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
```

Y en el vault de comunicaciones, la verificación del flujo de mejora con IA demuestra el
encadenamiento de dos mocks independientes (servicio de plantillas + servicio de IA):

```python
def test_mejorar_plantilla_exitosa_devuelve_200(client):
    with patch("app.h_vault_comunicaciones.routes.service.get_plantilla",
               return_value=_PLANTILLA_DICT), \
         patch("app.h_vault_comunicaciones.routes.ai_service.mejorar",
               return_value="texto mejorado"):
        resp = client.post(
            "/api/vault/plantillas/00000000-0000-0000-0000-000000000001/mejoras",
            headers=_auth(),
            json={"contenido": "hola", "idioma": "es"},
        )
    assert resp.status_code == 200
    assert resp.get_json()["contenido"] == "texto mejorado"
```

### 7.2.2. Pruebas unitarias de servicio — Backend

El módulo `tests/h_sincronizador_contactos/test_export_csv.py` agrupa las pruebas puras de la
función `export_csv` del servicio de sincronización de contactos. A diferencia de los tests de
integración de rutas, estas pruebas ejercen directamente la función de servicio sin pasar por la
capa HTTP, aislando todas las dependencias con `unittest.mock`:

```python
def test_export_csv_fechas_validas_llama_fetch_con_isoformat():
    pms_mock = MagicMock()
    pms_mock.fetch_reservations.return_value = []

    with (
        patch("app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
              return_value=_pms_config_mock()),
        patch("app.h_sincronizador_contactos.service.decrypt", return_value="api_key"),
        patch("app.h_sincronizador_contactos.service.build_pms_client",
              return_value=pms_mock),
        patch("app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
              return_value={}),
        patch("app.h_sincronizador_contactos.service.build_csv", return_value=b"Name,Phone\n"),
    ):
        csv_bytes, error = export_csv("empresa_1", {"desde": "2026-05-01", "hasta": "2026-05-31"})

    assert error is None
    assert csv_bytes == b"Name,Phone\n"
    pms_mock.fetch_reservations.assert_called_once_with(desde="2026-05-01", hasta="2026-05-31")


def test_export_csv_fecha_invalida_devuelve_error():
    csv_bytes, error = export_csv("empresa_1", {"desde": "no-es-fecha"})

    assert csv_bytes is None
    assert error == "Parámetros de fecha inválidos."
```

Además de `test_export_csv.py`, backend incorpora varias suites unitarias de servicio orientadas a
reglas de negocio y efectos laterales controlados mediante mocks:

| Suite de servicio | Casos | Comportamiento validado |
|---|---:|---|
| `backend/tests/common/notifications/test_mail_service.py` | 21 | Composición del email, ausencia de configuración y errores del envío HTTP a Mailgun mockeado |
| `backend/tests/contact/test_service_contact.py` | 5 | Validación y tratamiento del servicio de contacto sin depender de la capa HTTP |
| `backend/tests/solicitud/test_service_solicitud.py` | 7 | Flujo del servicio público de solicitud y control de reglas de negocio |
| `backend/tests/usuarios/test_service_usuarios.py` | 4 | Reglas de servicio para gestión de usuarios y coherencia de resultados |

Esto desplaza el foco de backend desde pruebas exclusivamente de rutas hacia una estrategia mixta:
contratos HTTP para seguridad y permisos, y pruebas de servicio para reglas de negocio reutilizables.

### 7.2.3. Pruebas unitarias — Frontend

El frontend utiliza el **builder `@angular/build:unit-test`** de Angular 19 (que internamente
delega en **Vitest**) con cobertura de Istanbul. Cada test se escribe con la API `describe`/`it`
de Jasmine y hace uso de `TestBed` para instanciar componentes y servicios en un contexto Angular
real pero ligero.

**Pruebas de servicios**  
Los servicios HTTP se prueban con `HttpClientTestingModule` y `HttpTestingController`, que
permiten interceptar las peticiones salientes y devolver respuestas controladas sin realizar
llamadas de red reales. Por ejemplo, `auth.service.spec.ts` verifica la decodificación del JWT
almacenado en `localStorage`:

```typescript
it('debería retornar false cuando el token está expirado', () => {
  const payload = { sub: 'user@test.com', exp: Math.floor(Date.now() / 1000) - 60 };
  const token = 'x.' + btoa(JSON.stringify(payload)) + '.sig';
  localStorage.setItem('auth_token', token);
  expect(service.isLoggedIn()).toBeFalse();
});

it('debería retornar true cuando el token es válido y no ha expirado', () => {
  const payload = { sub: 'user@test.com', exp: Math.floor(Date.now() / 1000) + 3600 };
  const token = 'x.' + btoa(JSON.stringify(payload)) + '.sig';
  localStorage.setItem('auth_token', token);
  expect(service.isLoggedIn()).toBeTrue();
});
```

**Pruebas del interceptor HTTP**  
`auth.interceptor.spec.ts` verifica que el interceptor funcional añade la cabecera
`Authorization: Bearer <token>` exclusivamente en las peticiones dirigidas a `/api/`,
sin afectar a llamadas a rutas externas:

```typescript
it('debería añadir el header Authorization a peticiones /api/', () => {
  localStorage.setItem('auth_token', 'token-de-prueba');
  let req!: HttpRequest<unknown>;
  const next = (r: HttpRequest<unknown>) => { req = r; return of(new HttpResponse()); };
  authInterceptor(new HttpRequest('GET', '/api/apartamentos'), next as never);
  expect(req.headers.get('Authorization')).toBe('Bearer token-de-prueba');
});

it('NO debería añadir Authorization a URLs que no contienen /api/', () => {
  localStorage.setItem('auth_token', 'token-de-prueba');
  let req!: HttpRequest<unknown>;
  const next = (r: HttpRequest<unknown>) => { req = r; return of(new HttpResponse()); };
  authInterceptor(new HttpRequest('GET', '/public/page'), next as never);
  expect(req.headers.get('Authorization')).toBeNull();
});
```

**Pruebas del guard de autenticación**  
`auth.guard.spec.ts` verifica las tres ramas del guard: acceso permitido, redirección a
`/login?acceso=requerido` cuando no hay sesión activa, y redirección a `/cambio-password` cuando
el JWT incluye el flag `debe_cambiar_password`:

```typescript
it('debería retornar false y redirigir a /login cuando el usuario no está autenticado', () => {
  spyOn(authService, 'isLoggedIn').and.returnValue(false);
  const result = guard(routeMock, stateMock);
  expect(result).toBeFalse();
  expect(router.navigate).toHaveBeenCalledWith(
    ['/login'],
    jasmine.objectContaining({ queryParams: { acceso: 'requerido' } }),
  );
});
```

**Pruebas de componentes UI**  
Los componentes atómicos y moleculares disponen de tests individuales que verifican sus
`@Input` (bindings de datos) y sus `@Output` (eventos emitidos). Por ejemplo,
`heatmap-grid.spec.ts` valida la lógica de agrupación de días en filas semanales y la asignación
de clases de intensidad de color según los umbrales configurados:

```typescript
it('debería crear dos filas para 14 días', () => {
  component.dias = Array.from({ length: 14 }, (_, i) => ({
    fecha: `2026-05-${String(i + 1).padStart(2, '0')}`,
    checkins: 0, checkouts: 0,
  }));
  fixture.detectChanges();
  expect(component.rows().length).toBe(2);
});

it('debería asignar clase i100 cuando checkins supera el nivel3', () => {
  component.umbrales = { nivel1: 2, nivel2: 4, nivel3: 6 };
  expect(component.intensidadClass(7)).toBe('i100');
});
```

La cobertura del frontend incluye además piezas como `tag.spec.ts`,
`how-it-works-button.spec.ts`, `theme-toggle.spec.ts`, `templates-card.spec.ts` y
`theme.service.spec.ts`. Con ello, la batería de tests deja de centrarse solo en CRUD, auth y
componentes base, y cubre también tema visual, onboarding, tarjetas compuestas y persistencia del
estado de interfaz.

### 7.2.4. Pruebas manuales de smoke y validaciones complementarias

Además de la exploración manual de integraciones externas, el proyecto mantuvo un guion de smoke
test específico para el módulo de mapa de calor. La comprobación manual se estructuró en tres
bloques:

1. **Caso A — con PMS conectado**: verifica badge de proveedor, generación de cuadrícula,
   representación del rango y ausencia de subida XLSX cuando la integración PMS está operativa.
2. **Caso B — sin PMS, con XLSX**: comprueba la configuración previa de columnas en perfil,
   la carga de ficheros y el funcionamiento del fallback manual.
3. **Caso C — validaciones**: fuerza errores esperables de usuario, como ausencia de fechas,
   configuración XLSX incompleta o umbrales inválidos en perfil.

Como validación no funcional complementaria, las auditorías WAVE documentadas en el capítulo 2 se
utilizaron como comprobación manual de accesibilidad. No forman parte de la suite automatizada,
pero sí de la evidencia de calidad revisada durante el cierre del proyecto.

---

## 7.3. Cobertura de código

### 7.3.1. Frontend — Istanbul / Vitest

La cobertura del frontend se genera automáticamente en cada ejecución de `ng test` gracias al
builder `@angular/build:unit-test`, que delega en **Istanbul** (integrado en Vitest) para la
instrumentación. El informe se produce en los formatos `text` (salida de consola), `html` y
`lcov`, y se sube como artefacto de CI con una retención de 14 días.

La configuración de umbrales mínimos se define en `vitest.config.ts`:

```typescript
// frontend/vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'istanbul',
      include: ['src/**/*.ts'],
      exclude: [
        'src/environments/**',
        'src/main.ts',
        'src/app/app.config.ts',
        '**/*.spec.ts',
        '**/*.d.ts',
      ],
      thresholds: {
        statements: 90,
        branches: 90,
        functions: 90,
        lines: 90,
      },
      reporter: ['text', 'html', 'lcov'],
    },
  },
});
```

Estos umbrales garantizan que cualquier *pull request* que reduzca la cobertura por debajo del
90 % en sentencias, ramas, funciones o líneas provoca un fallo en el pipeline de CI, impidiendo
su fusión. La exclusión de `src/app/pages/**` en `angular.json` elimina del cómputo las páginas
de la aplicación, cuya lógica es principalmente declarativa (enrutamiento y composición de
componentes).

### 7.3.2. Backend — pytest-cov

El pipeline de CI del backend (`ci-python.yml`) ejecuta `pytest backend/tests/ --cov=app
--cov-config=backend/.coveragerc --cov-fail-under=90` y publica el informe HTML como artefacto
con 14 días de retención. La configuración de exclusiones se define en
`backend/.coveragerc`:

```ini
[run]
source = app
omit =
    */__init__.py
    */tests/*
    */migrations/*
    */repository.py
    app/exceptions/*
    app/h_maestro_apartamentos/smoobu_client.py
    app/h_sincronizador_contactos/google_people_client.py
    app/h_vault_comunicaciones/ia_client.py
    app/normalizador_pms/*
    app/common/notifications/discord.py
    app/solicitud/turnstile.py
    app/common/ai_service.py
```

**Justificación de exclusiones**:

- **Repositorios** (`*/repository.py`): capa de acceso a datos basada en SQLAlchemy. Su
  validación real requiere integration tests con PostgreSQL, no unit tests con mocks. Sigue
  el mismo principio que `angular.json` aplica en frontend al excluir `src/app/pages/**`.
- **Adapters externos** (Smoobu, Google People, IA): son envoltorios sobre SDKs/APIs
  de terceros; se validan manualmente en entorno Docker local (ver 7.2.4).
- **Normalizadores PMS**: dependen de la forma exacta del JSON externo; se cubren mediante
  pruebas manuales con respuestas reales.
- **Turnstile/Discord**: integraciones HTTP simples sin lógica de negocio testable
  unitariamente.

Cualquier *pull request* que reduzca la cobertura por debajo del **90 %** falla el pipeline,
quedando alineada con el umbral aplicado al frontend (90 % en `vitest.config.ts`).

---

## 7.4. Resultados y estadísticas

Los resultados de esta sección miden la calidad del código validada mediante tests automatizados y
comprobaciones locales controladas. No equivalen a una certificación completa del despliegue en
Railway, pero el antiguo bloqueo del envío SMTP en producción dejó de aplicar tras migrar el
servicio de correo a Mailgun por HTTP con API key.

### 7.4.1. Desglose por suite — Backend

Backend suma **499 casos** repartidos en **33 archivos de test**, distribuidos entre
integración HTTP, unitarios de servicio y unitarios de helpers/parsers.

| Suite de pruebas | Tipo | Pruebas | Resultado |
|---|---|---|---|
| `tests/auth/test_routes_auth.py` | Integración (HTTP) | 7 | ✅ |
| `tests/auth/test_service_auth.py` | Unitaria de servicio | 12 | ✅ |
| `tests/auth/test_password_rules.py` | Unitaria | 20 | ✅ |
| `tests/empresas/test_routes_empresas.py` | Integración (HTTP) | 8 | ✅ |
| `tests/empresas/test_service_empresas.py` | Unitaria de servicio | 2 | ✅ |
| `tests/empresas/test_empresas_delete.py` | Unitaria | 5 | ✅ |
| `tests/empresas/test_repository_empresas.py` | Unitaria de repo | 3 | ✅ |
| `tests/usuarios/test_routes_usuarios.py` | Integración (HTTP) | 10 | ✅ |
| `tests/usuarios/test_service_usuarios.py` | Unitaria de servicio | 4 | ✅ |
| `tests/usuarios/test_service_usuarios_full.py` | Unitaria de servicio | 23 | ✅ |
| `tests/perfil/test_routes_perfil.py` | Integración (HTTP) | 9 | ✅ |
| `tests/perfil/test_service_perfil.py` | Unitaria de servicio | 8 | ✅ |
| `tests/perfil/test_service_perfil_extra.py` | Unitaria de servicio | 18 | ✅ |
| `tests/h_vault_comunicaciones/test_routes_vault.py` | Integración (HTTP) | 9 | ✅ |
| `tests/h_maestro_apartamentos/test_routes_apartamentos.py` | Integración (HTTP) | 9 | ✅ |
| `tests/h_maestro_apartamentos/test_routes_apartamentos_extra.py` | Integración (HTTP) | 33 | ✅ |
| `tests/h_maestro_apartamentos/test_service_apartamentos.py` | Unitaria de servicio | 32 | ✅ |
| `tests/h_maestro_apartamentos/test_xlsx_parser.py` | Unitaria de parser | 23 | ✅ |
| `tests/h_mapa_de_calor/test_routes_heatmap.py` | Integración (HTTP) | 2 | ✅ |
| `tests/h_mapa_de_calor/test_routes_heatmap_extra.py` | Integración (HTTP) | 30 | ✅ |
| `tests/h_mapa_de_calor/test_service_heatmap.py` | Unitaria de servicio | 27 | ✅ |
| `tests/h_notificaciones_tardias/test_routes_notificaciones.py` | Integración (HTTP) | 20 | ✅ |
| `tests/h_notificaciones_tardias/test_service_notificaciones.py` | Unitaria de servicio | 18 | ✅ |
| `tests/h_sincronizador_contactos/test_routes_contactos.py` | Integración (HTTP) | 34 | ✅ |
| `tests/h_sincronizador_contactos/test_service_full.py` | Unitaria de servicio | 42 | ✅ |
| `tests/h_sincronizador_contactos/test_contacto_formatter.py` | Unitaria de helper | 41 | ✅ |
| `tests/h_sincronizador_contactos/test_export_csv.py` | Unitaria de servicio | 3 | ✅ |
| `tests/contact/test_routes_contact.py` | Integración (HTTP) | 4 | ✅ |
| `tests/contact/test_service_contact.py` | Unitaria de servicio | 5 | ✅ |
| `tests/solicitud/test_routes_solicitud.py` | Integración (HTTP) | 6 | ✅ |
| `tests/solicitud/test_service_solicitud.py` | Unitaria de servicio | 7 | ✅ |
| `tests/common/notifications/test_mail_service.py` | Unitaria de servicio | 21 | ✅ |
| `tests/docs/test_routes_docs.py` | Integración (HTTP) | 4 | ✅ |
| **TOTAL** | — | **499** | **✅ 100 %** |

**Resumen global del backend:**

| Métrica | Valor |
|---|---|
| Total de pruebas | 499 |
| Pruebas exitosas | 499 |
| Fallos | 0 |
| Errores | 0 |
| Omitidas | 0 |
| Tasa de éxito | 100 % |
| Cobertura (`pytest-cov`) | **92 %** (umbral mínimo 90 %) |
| Archivos de test | 12 |
| Módulos cubiertos | auth, empresas, usuarios, perfil, vault, apartamentos, heatmap, contactos, solicitud, notificaciones |

Backend queda distribuido en **suites de integración HTTP**, **suites de servicio** y
**suites de helpers/parsers**, cubriendo seguridad/rutas, lógica de negocio reutilizable y
utilidades transversales con una cobertura efectiva del **92 %** sobre el código no excluido
(ver 7.3.2).

### 7.4.2. Desglose por spec — Frontend

Los **38 archivos `*.spec.ts`** cubren servicios, componentes (átomos, moléculas, organismos), el
guard de autenticación y el interceptor HTTP. La distribución por categoría es la siguiente:

| Categoría | Specs | Tests |
|---|---|---|
| Servicios (`auth`, `apartamentos`, `vault`, `mapa-calor`, `perfil`, `gestion-usuarios`, `contactos`, `sidenav`, `theme`) | 9 | 103 |
| Componentes organismos (`header`, `footer`, `sidenav`, `modal`, `tabla-crud`, `heatmap-grid`, `templates-card`) | 7 | 48 |
| Componentes moléculas (`alert`, `confirm-inline`, `accordion-item`, `form-field`, `form-input-icon`, `search-bar`, `dropdown-buscador`, `tarjeta-estado`, `how-it-works-button`, `theme-toggle`) | 10 | 75 |
| Componentes átomos (`button`, `badge`, `icon`, `form-input`, `form-select`, `form-label`, `form-textarea`, `form-checkbox`, `tag`) | 9 | 60 |
| Guards (`auth.guard`) | 1 | 4 |
| Interceptores (`auth.interceptor`) | 1 | 5 |
| App raíz (`app.spec`) | 1 | 2 |
| **TOTAL** | **38** | **297** |

**Resumen global del frontend:**

| Métrica | Valor |
|---|---|
| Total de pruebas | 297 |
| Pruebas exitosas | 297 |
| Fallos | 0 |
| Errores | 0 |
| Specs (archivos) | 38 |
| Tasa de éxito | 100 % |
| Umbral mínimo de cobertura | 90 % (sentencias, ramas, funciones, líneas) |

> Nota: el recuento excluye los archivos de páginas (`src/app/pages/**`) conforme a la
> configuración de exclusión de `angular.json`.

### 7.4.3. Integración continua

El repositorio dispone de **seis workflows principales** de validación, publicación y seguridad.

**CI Python (`ci-python.yml`)**  
Se ejecuta en cada *push* a `main` y en *pull requests*. Consta de dos trabajos secuenciales:

1. `lint` — Análisis estático con `ruff` sobre `backend/app/`.
2. `tests` — Ejecución de `pytest backend/tests/ -v` con Python 3.12. Este trabajo levanta un
   contenedor de servicio `postgres:16-alpine` con las variables `DATABASE_URL`, `SECRET_KEY` y
   `JWT_SECRET_KEY` inyectadas como variables de entorno, reproduciendo las condiciones reales de
   producción.

**CI Angular Tests (`ci-angular-tests.yml`)**  
Se ejecuta en *push* a cualquier rama y en *pull requests* a `main`. Consta de dos trabajos:

1. `test-frontend` — `npx ng test --watch=false` con Node 22. Genera el informe de cobertura en
   `frontend/coverage/` y lo sube como artefacto con 14 días de retención.
2. `deploy-check` — Build de producción (`npm run build`) tras pasar los tests, como verificación
   adicional de que el código es compilable.

**CI Angular Build (`ci-angular.yml`) y CI Web (`ci-web.yml`)**  
Validan, respectivamente, el build de producción de Angular y el build estático de 11ty.

**Publicación Docker (`docker-publish.yml`)**  
Se activa únicamente cuando los tres pipelines de CI (Python, Angular y Web) han finalizado con
éxito en el mismo SHA de commit. Un trabajo previo `verificar` consulta la API de GitHub para
comprobar las conclusiones de todos los workflows; solo si todos devuelven `"success"` se lanza el
trabajo `publicar`, que construye y publica las imágenes con etiquetas de SHA corto.

**Auditoría de seguridad (`trivy.yml`)**  
El workflow `Trivy Audit` se dispara en *pull requests* a `main`, en *push* a `main`, por
calendario semanal y manualmente (`workflow_dispatch`). El escaneo se hace sobre filesystem e IaC,
limita el resultado a severidades `HIGH` y `CRITICAL`, genera un informe SARIF, lo sube como
artefacto con 14 días de retención y lo publica además en GitHub Security.

| Pipeline | Disparador | Herramienta | Acción principal |
|---|---|---|---|
| `ci-python.yml` | Push/PR a `main` | Python 3.12 + pytest | Lint ruff + tests con postgres:16-alpine |
| `ci-angular-tests.yml` | Push a cualquier rama / PR a `main` | Node 22 + Vitest | Tests + artefacto de cobertura |
| `ci-angular.yml` | Push/PR a `main` | Node 22 + Angular CLI | Build de producción |
| `ci-web.yml` | Push/PR a `main` | Node 22 + 11ty | Build del sitio estático |
| `docker-publish.yml` | Tras éxito de los 3 CI en mismo SHA | Docker + GitHub API | Publicación de imágenes en Docker Hub |
| `trivy.yml` | PR/Push a `main`, semanal, manual | Trivy + SARIF | Escaneo de vulnerabilidades y misconfiguraciones con publicación en GitHub Security |
