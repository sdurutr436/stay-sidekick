# Proyección a futuro — Herramienta: Mapa de Calor

## Funcionalidades identificadas durante el desarrollo del MVP

### Interactividad de celdas
- Hover con tooltip mostrando número exacto de reservas y checkouts del día.
- Click en celda para ver detalle de qué apartamentos están en check-in o
  check-out ese día.

### Generación de cuadrantes de trabajo
- Exportar el mapa de calor como hoja de cálculo con los días, volumen de
  trabajo y asignación de personas por turno.
- Integración con la herramienta de cuadrantes que ya utilizan las empresas.

### Rango de fechas
- Limitar o avisar si el rango supera N meses (configurable por empresa).
- Permitir selección de fechas pasadas para análisis histórico de temporadas.

### Colores adicionales
- Azul celeste y amarillo mostaza reservados para métricas futuras
  (por ejemplo: ocupación simultánea, solapamientos de reservas).

### Histórico
- Vista de mapas de calor pasados para análisis de temporadas anteriores.
- Comparación lado a lado entre dos periodos distintos.

### Configuración por empresa
- (Implementado) Umbrales de color configurables en perfil de empresa.
- (Implementado) Columnas XLSX configurables en perfil de empresa (solo visible sin PMS).

### Mejoras de UX
- Estado de carga con skeleton en la cuadrícula mientras se generan los datos.
- Persistencia del último rango generado en sesión para no tener que
  reseleccionar fechas al volver a la página.
- Leyenda visual de la escala de colores junto a la cuadrícula.
