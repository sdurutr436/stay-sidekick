# 2. Descripcion

---

## Indice

- [2.1. Descripcion detallada de cada funcionalidad principal](#21-descripcion-detallada-de-cada-funcionalidad-principal)
  - [Autenticacion y control de acceso](#autenticacion-y-control-de-acceso)
  - [Arquitectura multiempresa y gestion de usuarios](#arquitectura-multiempresa-y-gestion-de-usuarios)
  - [Maestro de apartamentos](#maestro-de-apartamentos)
  - [Mapa de calor operativo](#mapa-de-calor-operativo)
  - [Notificaciones de check-in tardio](#notificaciones-de-check-in-tardio)
  - [Sincronizacion de contactos](#sincronizacion-de-contactos)
  - [Vault de comunicaciones asistido por IA](#vault-de-comunicaciones-asistido-por-ia)
  - [Perfil, integraciones y parametros por empresa](#perfil-integraciones-y-parametros-por-empresa)
  - [Formulario de contacto publico](#formulario-de-contacto-publico)
  - [Seguridad y cumplimiento transversal](#seguridad-y-cumplimiento-transversal)
- [2.2. Interfaz de usuario y experiencia de usuario (UI/UX)](#22-interfaz-de-usuario-y-experiencia-de-usuario-uiux)
  - [Principios de diseno](#principios-de-diseno)
  - [Estructura general de la interfaz](#estructura-general-de-la-interfaz)
  - [Pantallas y modulos principales](#pantallas-y-modulos-principales)
  - [Accesibilidad y diseno responsive](#accesibilidad-y-diseno-responsive)
  - [Feedback y manejo de errores](#feedback-y-manejo-de-errores)
- [2.3. Usuarios objetivo y casos de uso](#23-usuarios-objetivo-y-casos-de-uso)
  - [Perfiles de usuario](#perfiles-de-usuario)
  - [Casos de uso y flujos principales](#casos-de-uso-y-flujos-principales)
  - [Tabla resumen de casos de uso](#tabla-resumen-de-casos-de-uso)

## 2.1. Descripcion detallada de cada funcionalidad principal

Stay Sidekick es una plataforma satelite para operaciones del alquiler vacacional. Su objetivo no es sustituir el PMS, sino cubrir tareas operativas que suelen resolverse de forma manual o con herramientas dispersas.

### Autenticacion y control de acceso

La plataforma implementa autenticacion basada en token para proteger las areas privadas:

- Inicio de sesion mediante correo y contrasena.
- Emision de JWT con datos de sesion (usuario, empresa, rol).
- Validacion de token para endpoints protegidos.
- Proteccion CSRF en operaciones de escritura mediante patron Double-Submit Cookie.
- Limitacion de peticiones por IP en endpoints sensibles.

Este enfoque protege la sesion y evita que acciones criticas se ejecuten desde origanes no autorizados.

### Arquitectura multiempresa y gestion de usuarios

Cada usuario pertenece a una empresa y opera sobre sus propios datos. Esto permite trabajar con varios clientes en una sola plataforma sin mezclar informacion.

Capacidades clave:

- Separacion logica de datos por empresa (multi-tenant).
- Gestion de usuarios por empresa (alta, baja, cambio de rol y reseteo de contrasena).
- Gestion de empresas para perfiles superadmin.
- Permisos por rol para limitar acciones administrativas.

Con ello, cada cuenta dispone de su propio catalogo de configuraciones, usuarios y herramientas.

### Maestro de apartamentos

El maestro de apartamentos es la base operativa sobre la que trabajan el resto de modulos.

Funciones principales:

- Alta, consulta, edicion y baja logica de apartamentos.
- Sincronizacion de propiedades desde PMS (Smoobu en el MVP).
- Importacion masiva desde archivo XLSX como mecanismo de respaldo.
- Vista previa de importacion antes de persistir cambios.

Este modulo asegura que la informacion de inventario este centralizada y consistente para el resto de procesos.

### Mapa de calor operativo

El mapa de calor muestra la carga diaria de check-ins y check-outs en un rango de fechas.

Incluye:

- Generacion de mapa desde PMS.
- Generacion alternativa desde archivos XLSX de entradas y salidas.
- Parametrizacion de umbrales de intensidad por empresa.
- Configuracion de columnas para adaptarse a diferentes formatos de exportacion.

Su valor principal es visualizar picos de operacion para anticipar necesidades de personal y coordinacion.

### Notificaciones de check-in tardio

Este modulo ayuda a estandarizar la comunicacion con huespedes que llegan fuera de horario.

Capacidades:

- Deteccion de check-ins del dia para control operativo.
- Carga de check-ins desde XLSX cuando no hay integracion API.
- Gestion de plantillas de mensaje (crear, editar, eliminar).
- Configuracion por empresa de reglas y parametros de notificacion.

Reduce errores de comunicacion y acelera respuestas en escenarios de alta carga.

### Sincronizacion de contactos

La sincronizacion de contactos conecta la operacion diaria con Google Contacts.

Funciones incluidas:

- Conexion y desconexion de cuenta Google via OAuth.
- Sincronizacion de contactos desde PMS a Google.
- Flujo alternativo XLSX -> Google para operaciones sin API.
- Exportacion CSV para revisiones manuales o cargas externas.
- Preferencias de sincronizacion configurables por empresa.

Con esto, el equipo evita mantener agendas duplicadas y mejora la trazabilidad del contacto con huespedes.

### Vault de comunicaciones asistido por IA

El vault centraliza plantillas reutilizables para mensajes operativos y comerciales.

Caracteristicas destacadas:

- Catalogo de plantillas por categoria e idioma.
- CRUD completo con borrado logico.
- Asistente IA para mejora de redaccion.
- Traduccion asistida por IA a otros idiomas.
- Contadores de uso y configuracion segura de proveedor IA.

Este modulo acelera la generacion de mensajes consistentes, especialmente en equipos con alta rotacion o volumen.

### Perfil, integraciones y parametros por empresa

Desde el area de perfil y ajustes se gestiona la personalizacion tecnica de la cuenta.

Permite:

- Cambio de contrasena del usuario autenticado.
- Configuracion de integracion PMS.
- Configuracion de integracion IA.
- Ajuste de parametros funcionales (columnas XLSX, reglas de modulos, etc.).

La plataforma prioriza la configuracion sin codigo para adaptar herramientas a cada operativa real.

### Formulario de contacto publico

Stay Sidekick incluye un endpoint publico para contacto comercial y soporte inicial.

Medidas relevantes:

- Validacion de datos de formulario.
- Proteccion antispam con Turnstile.
- Rate limit por IP para prevenir abuso.

Este canal permite captar interes y gestionar consultas sin exponer la zona privada.

### Seguridad y cumplimiento transversal

La seguridad se aplica de forma horizontal en todos los modulos.

Medidas tecnicas clave:

- JWT para autenticacion de API.
- CSRF para operaciones de escritura.
- CORS restringido por origen permitido.
- Rate limiting por endpoint.
- Separacion de datos entre empresas.

A nivel de producto, el enfoque de Stay Sidekick tambien busca alinearse con RGPD y buenas practicas de privacidad en el tratamiento de datos operativos.

## 2.2. Interfaz de usuario y experiencia de usuario (UI/UX)

### Principios de diseno

La experiencia de uso se define por cuatro principios:

- Claridad operativa: la informacion importante se ve en pocos clics.
- Eficiencia: las tareas repetitivas se resuelven con flujos cortos.
- Coherencia: los modulos comparten patrones de navegacion y formularios.
- Escalabilidad: la interfaz permite crecer en herramientas sin romper el flujo principal.

### Estructura general de la interfaz

La solucion se organiza en dos superficies complementarias:

- Sitio web publico: landing, producto, empresa y legales.
- Aplicacion privada (SPA): panel operativo y modulos funcionales autenticados.

En la aplicacion privada se mantiene una estructura comun:

- Navegacion lateral o superior con acceso a herramientas.
- Area central dinamica segun el modulo activo.
- Formularios con validaciones y estados de carga.
- Mensajeria de feedback para confirmar operaciones o informar errores.

### Pantallas y modulos principales

| Area | Objetivo | Acciones principales |
|---|---|---|
| Login | Acceso seguro al entorno privado | Autenticarse y abrir sesion |
| Dashboard operativo | Punto de entrada al trabajo diario | Navegar a mapa de calor, notificaciones, contactos, vault y maestro |
| Maestro de apartamentos | Mantener inventario actualizado | Alta/edicion, sincronizacion PMS, importacion XLSX |
| Mapa de calor | Visualizar carga diaria | Consultar rango, ajustar umbrales, exportar lectura operativa |
| Notificaciones tardias | Gestionar comunicacion de llegadas fuera de horario | Revisar check-ins, editar plantillas y parametros |
| Sincronizador de contactos | Mantener agenda operativa | Conectar Google, sincronizar, exportar CSV |
| Vault de comunicaciones | Estandarizar mensajes | Crear plantillas, mejorar/traducir con IA |
| Perfil e integraciones | Parametrizar la cuenta | Cambiar contrasena y configurar PMS/IA |
| Administracion de usuarios | Gestion de equipo por empresa | Altas, roles, bajas y reseteo de contrasena |

### Accesibilidad y diseno responsive

La interfaz esta pensada para uso en escritorio y movil:

- Composicion responsive para recepcion, oficina y uso en movilidad.
- Tipografia legible y jerarquia visual clara.
- Controles de formulario con etiquetas y mensajes de validacion comprensibles.
- Objetivo de alineacion con criterios WCAG 2.1 AA.

### Feedback y manejo de errores

La UX incorpora estados de sistema explicitos para reducir incertidumbre:

- Indicadores de carga en operaciones de red.
- Mensajes de exito tras guardar cambios.
- Mensajes de error accionables (validacion, permisos, sesion expirada, limites de uso).
- Confirmaciones en acciones potencialmente destructivas.

Esto reduce friccion y mejora la confianza del usuario en contextos operativos de tiempo limitado.

## 2.3. Usuarios objetivo y casos de uso

### Perfiles de usuario

Stay Sidekick esta orientado a equipos y profesionales del alquiler vacacional.

**Administrador de empresa**

Responsable de configurar la cuenta de su empresa, gestionar usuarios y definir parametros de funcionamiento (PMS, IA, plantillas, umbrales y formatos de entrada).

**Personal operativo (recepcion/coordinacion)**

Usa diariamente los modulos de mapa de calor, notificaciones tardias, contactos y vault para resolver tareas repetitivas con rapidez.

**Superadmin de plataforma**

Gestiona empresas y supervisa el estado global del sistema, sin intervenir en la operativa diaria de cada cliente salvo tareas de soporte y alta nivel.

**Responsable comercial o soporte**

Interactua con la capa publica (landing y formulario de contacto) para captar nuevas cuentas o atender incidencias iniciales.

### Casos de uso y flujos principales

**CU-01. Iniciar sesion en la aplicacion**
El usuario introduce credenciales validas, obtiene token de sesion y accede al panel principal.

**CU-02. Gestionar usuarios de la empresa**
El administrador crea una cuenta, ajusta su rol y, si es necesario, resetea su contrasena temporal.

**CU-03. Registrar o actualizar apartamentos**
El usuario administrativo crea o edita apartamentos de forma manual o realiza importacion/sincronizacion masiva.

**CU-04. Importar apartamentos desde XLSX con vista previa**
El usuario sube un archivo, revisa los cambios detectados y confirma la importacion final.

**CU-05. Consultar mapa de calor desde PMS**
El usuario selecciona un rango de fechas y visualiza intensidad de entradas/salidas para planificar recursos.

**CU-06. Generar mapa de calor desde XLSX**
Si no hay API disponible, el usuario sube archivos de check-ins/check-outs y obtiene la misma visualizacion operativa.

**CU-07. Ajustar umbrales del mapa de calor**
El administrador modifica niveles de intensidad para adaptar el semaforo operativo a su volumen real.

**CU-08. Revisar check-ins tardios del dia**
El equipo operativo consulta estado y casos pendientes para preparar instrucciones de llegada fuera de horario.

**CU-09. Gestionar plantillas de notificaciones tardias**
El usuario crea o edita mensajes estandar para reducir tiempos de respuesta y mantener tono coherente.

**CU-10. Sincronizar contactos con Google**
El administrador conecta su cuenta Google y lanza sincronizacion para mantener agenda actualizada.

**CU-11. Exportar contactos a CSV**
El usuario descarga un CSV para auditoria, respaldo o integracion con otras herramientas.

**CU-12. Crear y mantener plantillas en el vault**
El equipo guarda mensajes recurrentes por categoria e idioma para reutilizarlos en operaciones diarias.

**CU-13. Mejorar o traducir plantilla con IA**
El usuario solicita al asistente IA una version refinada o traducida y decide si la guarda.

**CU-14. Configurar integraciones PMS e IA**
El administrador actualiza claves y parametros de integracion desde ajustes para habilitar funcionalidades.

**CU-15. Cambiar contrasena de perfil**
El usuario autenticado modifica su contrasena para mantener la cuenta segura.

**CU-16. Alta de empresa en modo superadmin**
El superadmin registra una nueva empresa para habilitar su acceso a la plataforma.

**CU-17. Enviar solicitud desde formulario de contacto publico**
Un usuario externo rellena el formulario, supera validacion antispam y envia su consulta.

### Tabla resumen de casos de uso

| Codigo | Caso de uso | Actor principal | Prioridad |
|:---:|---|---|:---:|
| CU-01 | Iniciar sesion en la aplicacion | Usuario autenticado | Alta |
| CU-02 | Gestionar usuarios de la empresa | Admin de empresa | Alta |
| CU-03 | Registrar o actualizar apartamentos | Admin de empresa | Alta |
| CU-04 | Importar apartamentos desde XLSX con vista previa | Admin de empresa | Alta |
| CU-05 | Consultar mapa de calor desde PMS | Personal operativo | Alta |
| CU-06 | Generar mapa de calor desde XLSX | Personal operativo | Alta |
| CU-07 | Ajustar umbrales del mapa de calor | Admin de empresa | Media |
| CU-08 | Revisar check-ins tardios del dia | Personal operativo | Alta |
| CU-09 | Gestionar plantillas de notificaciones tardias | Personal operativo | Alta |
| CU-10 | Sincronizar contactos con Google | Admin de empresa | Media |
| CU-11 | Exportar contactos a CSV | Personal operativo | Media |
| CU-12 | Crear y mantener plantillas en el vault | Personal operativo | Alta |
| CU-13 | Mejorar o traducir plantilla con IA | Personal operativo | Media |
| CU-14 | Configurar integraciones PMS e IA | Admin de empresa | Alta |
| CU-15 | Cambiar contrasena de perfil | Usuario autenticado | Alta |
| CU-16 | Alta de empresa en modo superadmin | Superadmin | Media |
| CU-17 | Enviar formulario de contacto publico | Usuario externo | Media |
