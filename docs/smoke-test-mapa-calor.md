# Smoke test — Mapa de Calor

## Requisitos previos

- Docker Compose levantado (`docker compose up`).
- Usuario administrador de prueba creado.
- (Opcional) Cuenta Smoobu con al menos 1 propiedad activa.

---

## Caso A — Con PMS conectado

1. Login como admin.
2. Ir a **Perfil → Mapa de Calor — Umbrales de color**.
   - Verificar que los tres inputs están pre-cargados (por defecto: 10, 20, 30).
   - Verificar que el texto descriptivo bajo cada input muestra los valores actuales.
3. Ir a **Herramienta → Mapa de Calor**.
4. Verificar badge "PMS conectado" con el nombre del proveedor.
5. Seleccionar fecha inicio = hoy, fecha fin = fin del mes actual.
6. Pulsar "Generar mapa de calor".
7. Verificar que la cuadrícula aparece con los días del mes.
8. Verificar que los días adyacentes (semanas que cruzan el límite del rango) tienen opacidad reducida.
9. Verificar que no aparecen botones de subida de XLSX.

---

## Caso B — Sin PMS, con XLSX

1. Login como admin.
2. Ir a **Perfil → Mapa de Calor — Columnas XLSX**.
   - Verificar que la sección aparece (solo visible sin PMS conectado).
   - Escribir el nombre exacto de la columna de check-ins en el input de texto.
   - Opcionalmente escribir el nombre de la columna de check-outs.
   - Pulsar "Guardar configuración XLSX".
   - Verificar alerta de éxito.
3. Ir a **Herramienta → Mapa de Calor**.
4. Verificar que NO aparece el badge de PMS.
5. Verificar que aparecen instrucciones y botones de subida de XLSX.
6. Subir XLSX de check-ins con la columna configurada.
7. Seleccionar rango de fechas.
8. Pulsar "Generar".
9. Verificar que la cuadrícula aparece.
10. Verificar que un día con 0 movimientos usa fondo neutro (sin color).
11. Verificar que un día con solo check-ins (checkouts = 0 en todos los días) ocupa altura completa con número centrado.

---

## Caso C — Validaciones

1. Intentar generar sin seleccionar fechas → el botón "Generar" debe estar desactivado.
2. Intentar generar sin PMS y sin subir XLSX → verificar mensaje de validación.
3. Intentar subir XLSX sin configurar la columna en perfil → verificar error 422 con mensaje claro ("Configura la columna de fecha de check-in en el perfil...").
4. En el perfil, intentar guardar umbrales con nivel1 ≥ nivel2 → verificar error inline antes de enviar.
5. En el perfil, intentar guardar umbrales con valor 0 → verificar error inline antes de enviar.
6. Verificar que la sección "Columnas XLSX" del mapa de calor NO aparece en el perfil cuando hay PMS conectado.
