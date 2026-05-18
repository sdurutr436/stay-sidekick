# Diagrama Entidad-Relación — Stay Sidekick

## Contexto del modelo

Stay Sidekick es una plataforma SaaS multitenant para operativa de alquiler vacacional. La entidad raíz es `EMPRESAS` (cada cliente de la plataforma). Todas las entidades operativas cuelgan de ella mediante `empresa_id` con `ON DELETE CASCADE`, garantizando aislamiento de datos por tenant.

Convenciones del diagrama:

- `PK` clave primaria, `FK` clave foránea, `UK` restricción `UNIQUE`.
- `||--o{` relación 1 a 0..N (FK obligatoria en la entidad débil).
- `||--o|` relación 1 a 0..1 (FK obligatoria + `UNIQUE`, máximo un registro por empresa).
- `|o--o{` relación 0..1 a 0..N (FK opcional con `ON DELETE SET NULL`).
- Cifrado Fernet aplicado a campos con sufijo `_cifrado` o `_cifrada` antes de persistir.

## Diagrama

## Notas sobre dominios y restricciones (no representables en Mermaid)

- `usuarios.rol` admite solo `admin` o `operativo` (`CHECK`). El acceso de superadministrador se expresa con el flag booleano `es_superadmin` en combinación con `rol = 'admin'`.
- `apartamentos.pms_origen` admite `smoobu`, `beds24`, `manual`, `xlsx`.
- `apartamentos` define un índice único parcial sobre `(empresa_id, id_pms)` cuando `id_pms IS NOT NULL` para evitar duplicados de PMS sin bloquear altas manuales.
- `configuracion_pms.proveedor` admite `smoobu`, `beds24`, `hostaway`, `cloudbeds`.
- `configuracion_ia.proveedor` admite `default`, `gemini`, `openai`, `claude`. Si `api_key_cifrada` es `NULL`, el sistema usa la clave Gemini compartida del proyecto (modelo BYOK opcional).
- `logs_sincronizacion.origen` admite `pms`, `google_contacts`, `xlsx`, `heatmap_pms`; `estado` admite `exito`, `error`, `parcial`.
- `mensajes_generados` no almacena datos personales de huéspedes (RGPD): los datos de contexto que el frontend envía se usan en memoria y se descartan tras generar la respuesta.
- `system_prompts` es una tabla global (sin `empresa_id`): contiene los prompts del sistema editables sin redeploy.
