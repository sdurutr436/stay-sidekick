# Issues — Sprint 24-30 abril 2026

> Todas las issues pertenecen al sprint semanal del 24 al 30 de abril de 2026.
> Prioridad: 1 = más alta. Horas = estimación.

---

## FEAT-01 · Maestro de apartamentos — Integración con backend
**Tags:** `frontend` `backend`
**Prioridad:** 1 · **Horas:** 6h
**Descripción:** Conectar la página de maestro de apartamentos al backend real, eliminar mocks y añadir paginación y permisos por rol.

### Hijas

#### FEAT-01.1 · Crear ApartamentosService
**Tags:** `frontend` `backend`
**Prioridad:** 1 · **Horas:** 1h
Servicio Angular stateless con interfaces y métodos HTTP para todo el CRUD de apartamentos.

#### FEAT-01.2 · Conectar tabla al backend y eliminar mocks
**Tags:** `frontend`
**Prioridad:** 1 · **Horas:** 2h
Carga real en `ngOnInit` con `forkJoin(listar(), getPmsStatus())`, eliminar `MOCK_APARTAMENTOS`.

#### FEAT-01.3 · Eliminar columna Estado de la tabla
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 0.5h
El endpoint ya devuelve solo activos; la columna Estado no aporta valor.

#### FEAT-01.4 · Paginación (PAGE_SIZE = 20)
**Tags:** `frontend`
**Prioridad:** 2 · **Horas:** 1h
Computed `apartamentosPaginados`, `totalPaginas`, controles visibles solo si hay más de una página.

#### FEAT-01.5 · Permisos por rol en maestro de apartamentos
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 1.5h
Admin ve XLSX, Añadir, Eliminar y checkboxes. Worker solo ve Sincronizar si `pmsActivo()`.

---

## FEAT-02 · Nuevos componentes UI reutilizables
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 4h
**Descripción:** Tres componentes nuevos en atomic design con SCSS desacoplado en ITCSS.

### Hijas

#### FEAT-02.1 · ModalComponent (organism)
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 1.5h
Overlay + panel con header, body y footer proyectado. Input `open`, output `cerrar`.

#### FEAT-02.2 · AccordionItemComponent (molecule)
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 1h
Basado en `<details>/<summary>`, inputs `titulo`, `count`, `abierto`.

#### FEAT-02.3 · ConfirmInlineComponent (molecule)
**Tags:** `frontend` `ui/ux`
**Prioridad:** 2 · **Horas:** 1h
Mensaje + botón Confirmar/Cancelar con estado `cargando`. Outputs `confirmado`, `cancelado`.

---

## FEAT-03 · Alta inline de apartamentos en tabla
**Tags:** `frontend` `ui/ux`
**Prioridad:** 3 · **Horas:** 3h
**Descripción:** Filas editables inline encima de los resultados. Validación de nombre, `forkJoin` de `crear()` por fila, cancelación y guardado.

---

## FEAT-04 · Borrado múltiple tolerante a fallos parciales
**Tags:** `frontend` `backend`
**Prioridad:** 3 · **Horas:** 2h
**Descripción:** `forkJoin` con `catchError` por id. Recarga lista siempre. Alerta warning/error si hubo fallos. Usa `app-confirm-inline`.

---

## FEAT-05 · Sincronización Smoobu desde maestro de apartamentos
**Tags:** `frontend` `backend`
**Prioridad:** 3 · **Horas:** 1.5h
**Descripción:** Botón Sincronizar con estado `sincronizando`, alerta autocerrable a 5s, extrae `res.resultado`.

---

## FEAT-06 · Importación XLSX con flujo de preview
**Tags:** `frontend` `backend`
**Prioridad:** 4 · **Horas:** 5h
**Descripción:** Flujo completo: seleccionar archivo → preview backend → modal con acordeones → confirmar → importar.

### Hijas

#### FEAT-06.1 · Endpoint POST /api/apartamentos/importacion/preview
**Tags:** `backend`
**Prioridad:** 4 · **Horas:** 2h
Parsea sin persistir. Clasifica filas en `nuevos`, `actualizados`, `sin_cambios` usando `repo.get_by_id_pms`. Rate limit 30/hour.

#### FEAT-06.2 · Modal de importación XLSX con accordions
**Tags:** `frontend` `ui/ux`
**Prioridad:** 4 · **Horas:** 2h
`ModalImportacionXlsxComponent` con `app-modal` + `app-accordion-item` para cada categoría.

#### FEAT-06.3 · Flujo completo preview → confirmar → importar
**Tags:** `frontend`
**Prioridad:** 4 · **Horas:** 1h
`previewXlsx` → abrir modal → `importarXlsx` si confirma → recargar lista.

---

## FEAT-07 · Configuración de columnas XLSX por empresa
**Tags:** `frontend` `backend` `database`
**Prioridad:** 5 · **Horas:** 5h
**Descripción:** Cada empresa puede indicar el número de columna donde su XLSX tiene ID externo, nombre, dirección y ciudad. Se guarda en `empresas.configuracion` JSONB sin migración.

### Hijas

#### FEAT-07.1 · Endpoints GET/PUT /api/perfil/xlsx-apartamentos
**Tags:** `backend`
**Prioridad:** 5 · **Horas:** 1.5h
Lee y escribe en `empresas.configuracion["xlsx_apartamentos"]`. Solo admin puede escribir.

#### FEAT-07.2 · Parser XLSX flexible por número de columna
**Tags:** `backend`
**Prioridad:** 5 · **Horas:** 2h
Cuando `col_id_externo > 0` y `col_nombre > 0` usa números de columna (1-indexado); si no, detecta por cabecera.

#### FEAT-07.3 · Widget de configuración XLSX en perfil
**Tags:** `frontend` `ui/ux`
**Prioridad:** 5 · **Horas:** 1.5h
Nuevo panel en Perfil con 4 inputs numéricos. 0 = auto-detectar por cabecera.

---

## FEAT-08 · Soporte de unidades con tipología compartida (id_pms)
**Tags:** `backend` `database`
**Prioridad:** 5 · **Horas:** 3h
**Descripción:** Apartamentos con el mismo `id_externo` (tipología) pero diferente `id_pms` (unidad). El upsert pasa a usar `id_pms` como clave.

### Hijas

#### FEAT-08.1 · Migración BD: añadir id_pms, cambiar constraint
**Tags:** `database` `backend`
**Prioridad:** 5 · **Horas:** 1h
Añade `id_pms VARCHAR(100)`, elimina UNIQUE `(empresa_id, id_externo)`, crea índice parcial único `(empresa_id, id_pms) WHERE id_pms IS NOT NULL`.

#### FEAT-08.2 · Upsert y preview usan id_pms como clave de lookup
**Tags:** `backend`
**Prioridad:** 5 · **Horas:** 1.5h
`repo.get_by_id_pms`, `repo.upsert_from_external` con `id_pms`. Smoobu: `id_pms = id_externo`.

#### FEAT-08.3 · Parser lee siempre columna 1 como id_pms
**Tags:** `backend`
**Prioridad:** 5 · **Horas:** 0.5h
Independiente de la configuración de columnas. Fallback a `id_externo` si la celda está vacía.

---

## FIX-01 · isAdmin como getter en AuthService
**Tags:** `frontend` `backend`
**Prioridad:** 1 · **Horas:** 0.5h
**Descripción:** Convertir `isAdmin()` de método a getter `get isAdmin` y actualizar todas las llamadas en la app (incluido `perfil.ts`).

---

## FIX-02 · Preview XLSX devuelve 422 con archivo sin columnas reconocidas
**Tags:** `backend`
**Prioridad:** 1 · **Horas:** 0.5h
**Descripción:** El endpoint de preview devolvía 422 cuando el parser no encontraba columnas válidas. Ahora devuelve 200 con los errores en `preview.errores` para que el modal los muestre.

---

## DEVOPS-01 · Setup Docker local para desarrollo sin credenciales reales
**Tags:** `devops`
**Prioridad:** 2 · **Horas:** 2h
**Descripción:** Stack completo local sin necesitar el `.env` de producción.

### Hijas

#### DEVOPS-01.1 · docker-compose.dev.yml y backend/.env.dev
**Tags:** `devops`
**Prioridad:** 2 · **Horas:** 1h
Override con credenciales ficticias (Turnstile bypass, Fernet de prueba) y auto-seed de BD.

#### DEVOPS-01.2 · Fix DuplicateTable en arranque Docker local
**Tags:** `devops` `database`
**Prioridad:** 2 · **Horas:** 1h
`stamp_alembic.sql` en `initdb.d` marca la migración inicial como aplicada para que Alembic no intente recrear tablas ya creadas por `schema.sql`.

---

## Resumen del sprint

| ID | Título | Tags | Prioridad | Horas |
|----|--------|------|-----------|-------|
| FEAT-01 | Maestro apartamentos — Integración backend | frontend, backend | 1 | 6h |
| FEAT-01.1 | Crear ApartamentosService | frontend, backend | 1 | 1h |
| FEAT-01.2 | Conectar tabla al backend | frontend | 1 | 2h |
| FEAT-01.3 | Eliminar columna Estado | frontend, ui/ux | 2 | 0.5h |
| FEAT-01.4 | Paginación PAGE_SIZE=20 | frontend | 2 | 1h |
| FEAT-01.5 | Permisos por rol | frontend, ui/ux | 2 | 1.5h |
| FEAT-02 | Nuevos componentes UI | frontend, ui/ux | 2 | 4h |
| FEAT-02.1 | ModalComponent | frontend, ui/ux | 2 | 1.5h |
| FEAT-02.2 | AccordionItemComponent | frontend, ui/ux | 2 | 1h |
| FEAT-02.3 | ConfirmInlineComponent | frontend, ui/ux | 2 | 1h |
| FEAT-03 | Alta inline de apartamentos | frontend, ui/ux | 3 | 3h |
| FEAT-04 | Borrado múltiple tolerante | frontend, backend | 3 | 2h |
| FEAT-05 | Sincronización Smoobu | frontend, backend | 3 | 1.5h |
| FEAT-06 | Importación XLSX con preview | frontend, backend | 4 | 5h |
| FEAT-06.1 | Endpoint preview backend | backend | 4 | 2h |
| FEAT-06.2 | Modal XLSX con accordions | frontend, ui/ux | 4 | 2h |
| FEAT-06.3 | Flujo preview → confirmar | frontend | 4 | 1h |
| FEAT-07 | Config columnas XLSX por empresa | frontend, backend, database | 5 | 5h |
| FEAT-07.1 | Endpoints GET/PUT xlsx-apartamentos | backend | 5 | 1.5h |
| FEAT-07.2 | Parser flexible por número columna | backend | 5 | 2h |
| FEAT-07.3 | Widget config XLSX en perfil | frontend, ui/ux | 5 | 1.5h |
| FEAT-08 | id_pms — tipología compartida | backend, database | 5 | 3h |
| FEAT-08.1 | Migración BD id_pms | database, backend | 5 | 1h |
| FEAT-08.2 | Upsert por id_pms | backend | 5 | 1.5h |
| FEAT-08.3 | Parser columna 1 = id_pms | backend | 5 | 0.5h |
| FIX-01 | isAdmin getter AuthService | frontend, backend | 1 | 0.5h |
| FIX-02 | Preview XLSX 422 | backend | 1 | 0.5h |
| DEVOPS-01 | Docker local dev setup | devops | 2 | 2h |
| DEVOPS-01.1 | docker-compose.dev.yml | devops | 2 | 1h |
| DEVOPS-01.2 | Fix DuplicateTable stamp | devops, database | 2 | 1h |

**Total estimado: ~48h**
