# Endpoints — Herramienta: Mapa de Calor

## Consumidos por el frontend Angular

| Método | Endpoint                    | Auth | Rol mínimo | Descripción |
|--------|-----------------------------|------|------------|-------------|
| GET    | /api/heatmap                | JWT  | worker     | Genera mapa desde PMS. Query params: `desde` y `hasta` (YYYY-MM-DD). Respuesta: `{ ok, dias[] }` |
| POST   | /api/heatmap/xlsx           | JWT  | worker     | Genera mapa desde XLSX. Multipart: `checkins` (obligatorio), `checkouts` (opcional), `desde`, `hasta`. Respuesta: `{ ok, dias[], warnings? }` |
| GET    | /api/heatmap/umbrales       | JWT  | worker     | Lee umbrales de intensidad de la empresa. Respuesta: `{ ok, umbrales: { nivel1, nivel2, nivel3 } }` |
| PUT    | /api/heatmap/umbrales       | JWT  | admin      | Guarda umbrales. Body: `{ nivel1, nivel2, nivel3 }`. Respuesta: `{ ok, umbrales }` |
| GET    | /api/heatmap/config-xlsx    | JWT  | worker     | Lee config columnas XLSX. Respuesta: `{ ok, config: { col_fecha_checkin, col_fecha_checkout } }` |
| PUT    | /api/heatmap/config-xlsx    | JWT  | admin      | Guarda config columnas XLSX. Body: `{ col_fecha_checkin, col_fecha_checkout }`. Respuesta: `{ ok, config }` |
| GET    | /api/apartamentos/pms       | JWT  | worker     | Estado conexión PMS. Respuesta: `{ ok, config: { proveedor, activo, endpoint, ultimo_sync } \| null }` |

### Estructura de `DiaCalor` (en `dias[]`)

```json
{
  "fecha": "2025-06-01",
  "checkins": 3,
  "checkouts": 2,
  "mesAdyacente": false
}
```

`mesAdyacente: true` indica que el día está fuera del rango [desde, hasta] pero
pertenece a la semana completa visible en la cuadrícula (lunes–domingo).

## Disponibles para otros módulos internos

Ninguno por ahora. Los datos del mapa de calor se procesan en memoria y no se
persisten, por lo que no hay endpoints de consulta histórica.

## Proyección futura

Ver `docs/proyeccion-futura-mapa-calor.md`.
