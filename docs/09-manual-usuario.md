# 9. Manual de usuario

## Índice

- [9.1. Introducción](#91-introducción)
- [9.2. Primeros pasos](#92-primeros-pasos)
  - [9.2.1. Acceso a la aplicación](#921-acceso-a-la-aplicación)
  - [9.2.2. Inicio de sesión](#922-inicio-de-sesión)
  - [9.2.3. Cambio de contraseña obligatorio](#923-cambio-de-contraseña-obligatorio)
- [9.3. Panel principal (Mis herramientas)](#93-panel-principal-mis-herramientas)
- [9.4. Maestro de apartamentos](#94-maestro-de-apartamentos)
  - [9.4.1. Vista general](#941-vista-general)
  - [9.4.2. Alta manual y edición](#942-alta-manual-y-edición)
  - [9.4.3. Sincronización con Smoobu](#943-sincronización-con-smoobu)
  - [9.4.4. Importación por XLSX](#944-importación-por-xlsx)
- [9.5. Sincronizador de contactos](#95-sincronizador-de-contactos)
  - [9.5.1. Escenarios de uso según integraciones](#951-escenarios-de-uso-según-integraciones)
  - [9.5.2. Exportación CSV](#952-exportación-csv)
  - [9.5.3. Sincronización con Google Contacts](#953-sincronización-con-google-contacts)
- [9.6. Notificaciones de check-in tardíos](#96-notificaciones-de-check-in-tardíos)
- [9.7. Mapa de calor](#97-mapa-de-calor)
- [9.8. Vault de comunicaciones](#98-vault-de-comunicaciones)
- [9.9. Perfil y gestión de usuarios](#99-perfil-y-gestión-de-usuarios)
- [9.10. Casos de uso típicos (paso a paso)](#910-casos-de-uso-típicos-paso-a-paso)
- [9.11. Preguntas frecuentes y solución de problemas](#911-preguntas-frecuentes-y-solución-de-problemas)

---

## 9.1. Introducción

Stay Sidekick es una aplicación web para operaciones de alquiler vacacional. Centraliza en un solo panel tareas que normalmente se hacen de forma dispersa: gestión de apartamentos, sincronización de contactos, control de check-ins tardíos, mapa de carga operativa y gestión de plantillas de comunicación.

La aplicación se usa desde navegador y está diseñada para perfiles operativos y administradores de empresa.

![Placeholder — pantalla de inicio de Stay Sidekick](assets/manual/01-login-portada-placeholder.png)
_Placeholder de captura: pantalla de acceso a la aplicación._

---

## 9.2. Primeros pasos

### 9.2.1. Acceso a la aplicación

1. Abre la URL pública de la aplicación (entorno productivo o staging).
2. Pulsa **Iniciar sesión** desde la cabecera del sitio.
3. Se abrirá la pantalla de login.

![Placeholder — acceso desde cabecera pública](assets/manual/02-acceso-desde-web-placeholder.png)
_Placeholder de captura: botón de acceso desde la web pública._

### 9.2.2. Inicio de sesión

1. Introduce tu correo y contraseña.
2. Pulsa **Iniciar sesión**.
3. Si las credenciales son correctas, entrarás al panel **Mis herramientas**.

Si intentas acceder a una ruta privada sin sesión, el sistema redirige automáticamente a `/login?acceso=requerido`.

![Placeholder — formulario login](assets/manual/03-login-form-placeholder.png)
_Placeholder de captura: formulario de inicio de sesión._

### 9.2.3. Cambio de contraseña obligatorio

En cuentas con marca de seguridad activa, tras autenticarte se redirige a **/cambio-password**.

1. Introduce la contraseña actual.
2. Introduce y confirma la nueva contraseña.
3. Guarda cambios para continuar al panel.

![Placeholder — cambio de contraseña](assets/manual/04-cambio-password-placeholder.png)
_Placeholder de captura: pantalla de cambio de contraseña obligatoria._

---

## 9.3. Panel principal (Mis herramientas)

Después de iniciar sesión llegas al panel principal:

- Cabecera: **Mis herramientas**.
- Estado de integraciones: chips de **Google**, **PMS** e **IA**.
- Tarjetas de acceso rápido a cada módulo.
- En cuentas nuevas, bloque de **Primeros pasos** con enlaces directos a Perfil.

![Placeholder — dashboard mis herramientas](assets/manual/05-dashboard-mis-herramientas-placeholder.png)
_Placeholder de captura: panel principal con tarjetas y estado de integraciones._

---

## 9.4. Maestro de apartamentos

### 9.4.1. Vista general

El módulo **Maestro de apartamentos** centraliza el catálogo de propiedades de la empresa.

Funciones visibles:

- Buscador por nombre, ciudad o dirección.
- Tabla de apartamentos con origen e ID externo.
- Paginación.
- Acciones de alta, importación y sincronización (según permisos/estado).

![Placeholder — listado de apartamentos](assets/manual/06-maestro-listado-placeholder.png)
_Placeholder de captura: tabla principal del maestro._

### 9.4.2. Alta manual y edición

1. Pulsa **Añadir apartamento**.
2. Completa nombre (obligatorio) y campos opcionales.
3. Usa **Guardar cambios** para persistir.
4. Para editar registros existentes, selecciona la fila y aplica cambios.

![Placeholder — alta manual apartamento](assets/manual/07-maestro-alta-manual-placeholder.png)
_Placeholder de captura: fila de creación/edición en tabla CRUD._

### 9.4.3. Sincronización con Smoobu

Si hay PMS activo:

1. Pulsa **Sincronizar Smoobu**.
2. Espera el resultado.
3. Revisa el aviso de éxito/error en la alerta superior.

![Placeholder — sincronizar smoobu](assets/manual/08-maestro-sync-smoobu-placeholder.png)
_Placeholder de captura: botón y resultado de sincronización PMS._

### 9.4.4. Importación por XLSX

1. Pulsa **Importar XLSX**.
2. Selecciona el archivo.
3. Revisa la vista previa en el modal de importación.
4. Confirma para aplicar cambios.

![Placeholder — importación xlsx apartamentos](assets/manual/09-maestro-importacion-xlsx-placeholder.png)
_Placeholder de captura: modal de importación con preview._

---

## 9.5. Sincronizador de contactos

### 9.5.1. Escenarios de uso según integraciones

El módulo adapta sus acciones según dos estados: conexión PMS y conexión Google.

Estados posibles:

- PMS conectado + Google conectado: sincronización directa PMS -> Google.
- PMS conectado + Google desconectado: exportación CSV.
- PMS desconectado + Google conectado: sincronización XLSX -> Google.
- PMS desconectado + Google desconectado: exportación CSV desde XLSX.

![Placeholder — sincronizador contactos](assets/manual/10-contactos-vista-general-placeholder.png)
_Placeholder de captura: pantalla del sincronizador con chips de estado._

### 9.5.2. Exportación CSV

1. Define rango de fechas (si hay PMS) o sube archivo XLSX (si no hay PMS).
2. Pulsa **Descargar CSV**.
3. El archivo se descarga con los contactos normalizados.

![Placeholder — exportación csv contactos](assets/manual/11-contactos-export-csv-placeholder.png)
_Placeholder de captura: acción de exportación CSV._

### 9.5.3. Sincronización con Google Contacts

1. Verifica que Google está conectado desde Perfil.
2. Define rango (PMS) o sube XLSX.
3. Pulsa **Sincronizar con Google** / **Sincronizar PMS con Google**.
4. Revisa alerta de resultado.

![Placeholder — sync google contacts](assets/manual/12-contactos-sync-google-placeholder.png)
_Placeholder de captura: sincronización con Google Contacts._

---

## 9.6. Notificaciones de check-in tardíos

Este módulo permite preparar mensajes para llegadas fuera de horario.

Flujo recomendado:

1. Cargar check-ins del día (desde PMS o XLSX).
2. Seleccionar o crear una plantilla.
3. Insertar variables (nombre, apartamento, hora, dirección, etc.).
4. Generar mensaje automáticamente o editarlo manualmente.
5. Copiar mensaje final para enviarlo por el canal operativo.

![Placeholder — notificaciones checkin tardío](assets/manual/13-notificaciones-checkin-placeholder.png)
_Placeholder de captura: vista con plantillas y editor de mensaje._

---

## 9.7. Mapa de calor

El **Mapa de calor** visualiza carga de check-ins/check-outs por día.

Flujo de uso:

1. Selecciona **Fecha inicio** y **Fecha fin**.
2. Si no hay PMS activo, sube XLSX de check-ins (obligatorio) y check-outs (opcional).
3. Pulsa **Generar mapa de calor**.
4. Revisa la cuadrícula de intensidad en la sección **Resultados**.

![Placeholder — mapa de calor configuracion](assets/manual/14-mapa-calor-config-placeholder.png)
_Placeholder de captura: panel de configuración y subida de ficheros._

![Placeholder — mapa de calor resultados](assets/manual/15-mapa-calor-resultados-placeholder.png)
_Placeholder de captura: rejilla de resultados del mapa de calor._

---

## 9.8. Vault de comunicaciones

El vault centraliza plantillas reutilizables para mensajes operativos.

Acciones principales:

- Crear plantilla nueva.
- Buscar por categoría/idioma.
- Editar o eliminar plantilla.
- Mejorar redacción con IA.
- Traducir contenido a otro idioma.

![Placeholder — vault comunicaciones listado](assets/manual/16-vault-listado-placeholder.png)
_Placeholder de captura: listado de plantillas del vault._

![Placeholder — vault asistente IA](assets/manual/17-vault-ia-placeholder.png)
_Placeholder de captura: mejora/traducción asistida por IA._

---

## 9.9. Perfil y gestión de usuarios

### Perfil

Desde **Perfil** puedes:

- Cambiar contraseña.
- Configurar integración PMS.
- Configurar integración IA.
- Conectar/desconectar Google Contacts.
- Ajustar configuración XLSX y parámetros funcionales por empresa.

![Placeholder — perfil integraciones](assets/manual/18-perfil-integraciones-placeholder.png)
_Placeholder de captura: sección de integraciones en perfil._

### Gestión de usuarios (admin/superadmin)

Desde **Gestión de usuarios** puedes:

- Listar usuarios de la empresa.
- Crear usuario.
- Cambiar rol.
- Resetear contraseña.
- Eliminar usuario.

![Placeholder — gestion usuarios](assets/manual/19-gestion-usuarios-placeholder.png)
_Placeholder de captura: pantalla de administración de usuarios._

---

## 9.10. Casos de uso típicos (paso a paso)

### Caso 1 — Cargar apartamentos iniciales de una empresa

1. Entra a **Maestro de apartamentos**.
2. Pulsa **Importar XLSX**.
3. Revisa preview.
4. Confirma importación.
5. Valida que aparecen en la tabla.

### Caso 2 — Preparar comunicación de check-in tardío

1. Entra a **Notificaciones de check-in tardíos**.
2. Obtén check-ins del día (PMS o XLSX).
3. Selecciona plantilla.
4. Pulsa **Generar automáticamente**.
5. Ajusta texto y copia mensaje final.

### Caso 3 — Obtener agenda de huéspedes para recepción

1. Entra a **Sincronizador de contactos**.
2. Define rango (o sube XLSX).
3. Pulsa **Sincronizar con Google** si está conectado.
4. Si no, pulsa **Descargar CSV**.

### Caso 4 — Planificar carga semanal del equipo

1. Entra a **Mapa de calor**.
2. Selecciona rango de la próxima semana/mes.
3. Genera el mapa.
4. Revisa días de máxima intensidad para ajustar turnos.

---

## 9.11. Preguntas frecuentes y solución de problemas

**No puedo entrar, me devuelve a login continuamente.**  
Revisa que el usuario/contraseña sean correctos y que el token no esté expirado. Si vienes de un enlace interno sin sesión activa, el sistema redirige a `/login?acceso=requerido` de forma intencionada.

**Me redirige a cambio de contraseña y no al menú.**  
Tu cuenta tiene activada la obligación de actualizar credenciales. Cambia la contraseña y vuelve a iniciar sesión.

**No aparece “Sincronizar Smoobu” en Maestro de apartamentos.**  
Verifica permisos (admin) y que la integración PMS esté configurada en Perfil.

**La importación XLSX da error o no carga filas.**  
Comprueba formato de columnas y que el archivo sea `.xlsx`. Si el problema persiste, revisa la configuración de mapeo XLSX en Perfil.

**En Sincronizador no me deja enviar a Google.**  
Asegúrate de que la cuenta Google está conectada y autorizada. Si no lo está, el módulo solo mostrará exportación CSV.

**En Notificaciones no salen check-ins del día.**  
Puede no haber datos para la fecha/corte actual o puede fallar PMS. Importa XLSX manualmente para operar en modo alternativo.

**El mapa de calor no genera resultados.**  
Verifica rango de fechas, conexión PMS o carga de archivo check-ins (obligatorio en modo XLSX). Revisa también la configuración de columnas.

**No puedo crear usuarios aunque veo la pantalla.**  
La gestión de usuarios está limitada por rol (admin/superadmin). Si tu rol no tiene permisos, solicita alta de privilegios.

**Las funciones de IA no responden en Vault.**  
Comprueba estado de configuración IA en Perfil y límites de uso diarios. Si el proveedor externo falla, reintenta más tarde.

---

## Nota sobre capturas (placeholders)

Este documento incluye placeholders de imagen en `assets/manual/` para mantener la estructura de entrega aunque todavía no estén todas las capturas definitivas. Sustituye cada placeholder por su captura real manteniendo el mismo nombre de archivo para no tener que editar el manual.
