# Propuesta de mejora: Dashboard principal

**Rama:** `dev-dashboard`  
**Fecha:** 2026-05-06  
**Estado actual:** MVP funcional — barra de estado + grid de 5 herramientas.

---

## Problema

El dashboard actual cumple su función mínima (orientar al usuario y mostrar el estado de las conexiones), pero carece de contexto operativo. Un usuario que entra por primera vez —o cada mañana antes de trabajar— no sabe qué hay pendiente, cuántos apartamentos tiene registrados, ni si el sistema está operativo sin navegar a cada herramienta individualmente.

---

## Propuestas por bloques

### 1. Contador de recursos en cada card de herramienta

**Qué:** Añadir un número pequeño debajo del nombre de la herramienta indicando el volumen de datos gestionado.

| Herramienta | Contador |
|---|---|
| Maestro de apartamentos | N apartamentos registrados |
| Vault de comunicaciones | N plantillas activas |
| Notificaciones check-in | N plantillas de notificación |

**Cómo:** Llamar a `GET /api/apartamentos` (ya existe en `ApartamentosService`), `GET /api/vault/plantillas` (ya existe en `VaultService`). Añadir `contador?: number` a la interfaz `Herramienta`. Mostrarlo en el card como `<span class="dashboard__card-count">`.

**Por qué:** Da sensación de masa crítica al usuario y confirma que los datos están cargados sin necesidad de entrar en cada herramienta.

---

### 2. Indicador de disponibilidad condicionada por herramienta

**Qué:** Algunas herramientas requieren conexiones activas para funcionar al 100%. Mostrar un badge "Disponible" / "Limitado" / "No disponible" en cada card según el estado real de las integraciones.

| Herramienta | Requisito |
|---|---|
| Sincronizador de contactos | Requiere Google o PMS para modo completo |
| Mapa de calor | Funciona siempre (XLSX o PMS) |
| Notificaciones check-in | Funciona siempre (XLSX o PMS) |
| Vault de comunicaciones | IA opcional (mejora la experiencia) |
| Maestro de apartamentos | PMS opcional (para sincronización) |

**Cómo:** Con los datos de `IntegracionesData` ya cargados en `ngOnInit`, calcular el estado de cada herramienta como un `computed()` o una función `getEstadoHerramienta(id): 'ok' | 'parcial' | 'sin-conexion'`. Sin llamadas extra al backend.

**Por qué:** Evita que el usuario entre en Sincronizador de Contactos y no entienda por qué no aparece el botón de sincronizar directa.

---

### 3. Resumen de uso de IA

**Qué:** Si el usuario usa el sistema compartido de IA, mostrar en la barra de estado cuántas llamadas lleva hoy / esta semana respecto al límite.

```
IA  · Sistema compartido  ·  3/10 llamadas hoy
```

**Cómo:** El endpoint `GET /api/vault/uso-ia` ya devuelve `{ uso_hoy, limite_diario, uso_semana, limite_semanal }`. Se usa en `vault-comunicaciones`. Reutilizar en el dashboard si `datos.ia.configurado === false` (sistema compartido).

**Por qué:** El límite de IA compartida es la principal restricción de uso. El usuario necesita saber si le quedan créditos antes de abrir el Vault.

---

### 4. Nombre de usuario y rol en el encabezado del dashboard

**Qué:** Mostrar el email del usuario y su rol (Admin / Usuario) justo bajo el `app-page-header`.

```
Conectado como: alberto@empresa.com  ·  Administrador
```

**Cómo:** `AuthService` ya expone `user` (email y rol). No requiere llamada extra al backend.

**Por qué:** Útil en empresas con varios usuarios comparte cuenta. Confirma bajo qué perfil se está trabajando sin ir a Perfil.

---

### 5. Acceso directo a Perfil desde el dashboard

**Qué:** Dado que Perfil se eliminó del sidenav (es configuración, no herramienta), añadir un enlace o botón discreto en el footer o esquina del dashboard.

```
[Ir a Perfil →]   (variant ghost, alineado a la derecha)
```

**Cómo:** `<a routerLink="/perfil">` con `app-button variant="ghost"`. Cero lógica adicional.

**Por qué:** Sin Perfil en el sidenav, el usuario no tiene ruta visible hacia la configuración de integraciones desde el dashboard.

---

### 6. Estado vacío guiado ("empty state")

**Qué:** Si no hay ninguna integración configurada, reemplazar la barra de estado por un panel de bienvenida con pasos numerados.

```
Bienvenido a Stay Sidekick
Para empezar, conecta tus herramientas:
  1. Configura un PMS (Smoobu, Beds24…) en Perfil → Integraciones
  2. Conecta Google Contacts para sincronizar huéspedes
  3. Activa IA propia si quieres usar tu propio modelo
```

**Cómo:** Con `integraciones()` ya cargado, basta un `computed()`:
```typescript
readonly sinConexiones = computed(() => {
  const d = this.integraciones();
  return d && !d.pms.configurado && !d.google.configurado && !d.ia.configurado;
});
```

**Por qué:** Reduce el tiempo de "onboarding" de un usuario nuevo. El dashboard vacío actual no explica qué hacer a continuación.

---

## Prioridad sugerida

| # | Propuesta | Esfuerzo | Impacto |
|---|---|---|---|
| 5 | Acceso a Perfil desde dashboard | Muy bajo | Alto (necesario ya) |
| 4 | Nombre y rol del usuario | Muy bajo | Medio |
| 6 | Empty state guiado | Bajo | Alto |
| 2 | Badge disponibilidad por herramienta | Bajo | Alto |
| 3 | Resumen uso IA | Bajo | Medio |
| 1 | Contadores en cards | Medio | Medio |

---

## Datos disponibles sin endpoints nuevos

- `AuthService.user` → email, rol
- `PerfilService.getIntegraciones()` → ya se llama en `ngOnInit`
- `VaultService.getPlantillas()` → conteo de plantillas
- `ApartamentosService.getApartamentos()` → conteo de apartamentos

Las propuestas 4, 5 y 6 no requieren ninguna llamada adicional al backend. Las propuestas 1 y 3 reutilizan endpoints ya implementados.
