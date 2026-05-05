# 2. Descripción del sistema

Stay Sidekick es una plataforma web multi-empresa que actúa como capa satélite sobre los sistemas PMS del sector del alquiler vacacional. No sustituye al PMS, sino que cubre los huecos operativos que estos no resuelven o resuelven de forma poco práctica. Las empresas acceden a un catálogo personalizado de herramientas cuyo comportamiento es parametrizable sin modificar el código base, gracias a un motor de configuración propio que persiste las preferencias por cuenta de forma independiente.

---

## 2.1. Descripción detallada de cada funcionalidad principal

### 2.1.1. Herramienta 1 — Mapa de calor de entradas y salidas

**Propósito.** Proporcionar una vista rápida de la carga operativa diaria: cuántas llegadas y salidas se producen cada día dentro de un rango de fechas. Resuelve la necesidad cotidiana de anticipar picos de trabajo para coordinar al equipo de limpieza, recepción y mantenimiento sin tener que consultar el PMS herramienta por herramienta.

**Flujo funcional.** El usuario selecciona un rango de fechas mediante un selector de calendario (flatpickr) y elige la fuente de datos. Si la empresa tiene un PMS conectado, la generación es directa: el sistema consulta la API del proveedor y devuelve los datos procesados. Si no hay PMS configurado, el usuario sube un archivo XLSX con las reservas exportadas manualmente. El resultado se presenta como una cuadrícula tipo heatmap en la que cada celda representa un día: la mitad superior muestra el número de check-ins en verde con intensidad variable, y la mitad inferior muestra los check-outs en rojo con la misma escala. La intensidad se determina cruzando el valor del día con cuatro umbrales configurables.

**Fuentes de datos y fallback.** PMS conectado (Smoobu como proveedor de referencia en el MVP) → XLSX exportado del PMS como fallback. Si no hay ninguna fuente disponible, la herramienta muestra un error guiado.

**Configurabilidad.** El administrador de la empresa puede ajustar los cuatro umbrales de intensidad visual y los índices de columna del archivo XLSX (fecha de check-in y fecha de check-out) desde el panel de configuración.

**Restricciones.** Los datos de reservas procesados no se persisten en base de datos; todo el tratamiento se realiza en memoria en cumplimiento con el RGPD.

---

### 2.1.2. Herramienta 2 — Notificaciones para check-ins tardíos

**Propósito.** Detectar automáticamente las reservas con llegada posterior a la hora límite establecida por la empresa y generar un mensaje de notificación listo para enviar al huésped o al servicio de cambio de turno. Elimina el proceso manual de revisar reserva por reserva para identificar llegadas tardías y redactar el mensaje correspondiente.

**Flujo funcional.** Al acceder a la herramienta, el sistema devuelve el estado actual: si hay PMS conectado, carga automáticamente las reservas con check-in en el día de hoy y filtra las que superan la hora de corte. Si no hay PMS, el usuario sube un XLSX con las reservas. En ambos casos, la lista de check-ins tardíos se presenta agrupada por apartamento. El usuario selecciona una plantilla de la categoría `CHECKIN_TARDIO` del vault de comunicaciones (o una plantilla específica de la herramienta), el sistema aplica los tokens de la reserva y genera el mensaje final, listo para copiar y enviar por WhatsApp, email o SMS de forma manual.

**Fuentes de datos y fallback.** PMS conectado → XLSX temporal en sesión.

**Configurabilidad.** La hora de corte es configurable por empresa (valor por defecto: 20:00).

**Restricciones.** Los datos de huéspedes procesados en esta herramienta no se almacenan; se destruyen al finalizar la sesión HTTP (RGPD).

---

### 2.1.3. Herramienta 3 — Sincronización con Google Contacts

**Propósito.** Automatizar la creación y actualización de contactos en Google Contacts a partir de los datos de reserva, reemplazando el proceso manual de copiar nombre, teléfono y apartamento uno a uno. El fallback de exportación CSV permite el mismo resultado en entornos sin cuenta Google conectada.

**Flujo funcional.** El administrador de la empresa autoriza el acceso a la cuenta de Google de la empresa (donde existe el numero de WhatsApp por el que se comunican con huéspedes) mediante el flujo estándar OAuth 2.0 (pantalla de consentimiento de Google, intercambio de código por tokens). Una vez conectado, el usuario selecciona el rango de fechas y la fuente de datos (PMS o XLSX). El sistema agrupa los contactos por combinación nombre-teléfono —consolidando múltiples reservas del mismo huésped en un único contacto—, aplica la plantilla de nombre configurada y ejecuta un upsert en Google People API (búsqueda por teléfono; si existe, actualiza; si no, crea). Si Google no está conectado, la misma lógica genera un archivo CSV con las cabeceras exactas que Google requiere para importación manual.

**Fuentes de datos y fallback.** PMS API → XLSX. Para la salida: Google People API → CSV descargable.

**Configurabilidad.** Plantilla de nombre compuesto con tokens `{FECHA}`, `{APT}` y `{NOMBRE}`; separador de apartamentos cuando un huésped tiene varias reservas; formato de la fecha de entrada en las notas del contacto (seis variantes); índices de columna para la lectura del XLSX de reservas.

**Restricciones.** Los tokens de OAuth se almacenan cifrados con Fernet. Los datos personales de huéspedes no se persisten en base de datos (RGPD). La conexión con Google solo puede ser gestionada por el rol administrador.

---

### 2.1.4. Herramienta 4 — Base de datos de alojamientos

**Propósito.** Mantener un catálogo maestro de apartamentos por empresa con identificador único, nombre, dirección y ciudad. Este catálogo es la fuente de referencia que el resto de herramientas utilizan para enriquecer los datos de reserva con el nombre y dirección del alojamiento correspondiente, cruzando por el identificador externo del PMS.

**Flujo funcional.** El usuario dispone de un CRUD completo para gestionar los apartamentos de forma manual. Adicionalmente, puede lanzar una sincronización directa con la API del PMS conectado en ese momento, que extrae las propiedades activas de la cuenta y las inserta o actualiza en el catálogo local mediante upsert. Como alternativa, se ofrece la importación desde XLSX, también con upsert, para casos en los que el PMS no disponga de API o la empresa prefiera mantener el control manual.

**Fuentes de datos.** Alta manual → sincronización PMS → importación XLSX. La jerarquía se aplica en la misma sesión de trabajo: los datos del PMS sobreescriben los manuales si el identificador externo coincide.

**Configurabilidad.** La configuración del PMS (proveedor, API key cifrada, endpoint) se gestiona desde el perfil de la empresa. Cada empresa tiene un único PMS activo en cada momento.

---

### 2.1.5. Herramienta 5 — Vault de comunicaciones y generador IA

**Propósito.** Centralizar todas las plantillas de mensajes de la empresa en una biblioteca estructurada y ofrecer una capa de asistencia IA que adapta el contenido de la plantilla seleccionada al contexto concreto: ajuste de tono, traducción al idioma del huésped o generación de variaciones. La IA trabaja siempre sobre las plantillas definidas por la empresa, sin generar contenido desde cero.

**Flujo funcional.** El usuario navega por las plantillas organizadas por categoría (BIENVENIDA, INSTRUCCIONES, RECORDATORIO, CHECKIN\_TARDIO, CHECKOUT, INCIDENCIA, GENERAL) e idioma. Al seleccionar una, puede insertar placeholders desde un desplegable buscador (`{NOMBRE}`, `{APARTAMENTO}`, `{HORA_LLEGADA}`, `{IDIOMA}`, `{PROTOCOLO_CHECKIN}`) y editar el texto en un área de edición. Desde esa misma vista, el usuario puede invocar dos acciones IA: *mejorar* (refina el tono y la redacción en el idioma de la plantilla) o *traducir* (traduce el contenido a otro idioma). El resultado se muestra en el área de edición y puede copiarse al portapapeles con un clic. Un cooldown de 60 segundos entre llamadas IA evita el abuso accidental.

**Configurabilidad.** La configuración IA de la empresa determina el proveedor utilizado: por defecto se emplea Gemini 2.0 Flash con cuota compartida del sistema (con límites diario y semanal). Las empresas que deseen cuota ilimitada pueden aportar su propia API key (BYOK) para Gemini, OpenAI o Claude, gestionada desde el perfil.

**Restricciones.** Las API keys externas se almacenan cifradas. Los system prompts del servicio IA son editables únicamente desde IPs en lista blanca, protegiendo la coherencia del comportamiento del modelo.

---

### 2.1.6. Sistema de autenticación y gestión multi-empresa

El panel de administración está protegido por un sistema de autenticación basado en JWT firmados con HS256. Las contraseñas se almacenan con bcrypt. El endpoint de login aplica rate limiting estricto (10 peticiones por hora por IP) y validación CSRF mediante el patrón Double-Submit Cookie. Nginx actúa como proxy inverso y delega la verificación del token a un endpoint interno (`/api/auth/verify`) mediante la directiva `auth_request`, de modo que ninguna petición al backend alcanza los controladores sin un JWT válido.

Cada token incluye en sus claims el identificador de empresa y el rol del usuario (`admin` o `usuario`). Esta información se utiliza en cada endpoint para aplicar las restricciones de acceso pertinentes: la configuración del PMS, la conexión con Google y los umbrales del heatmap están reservados al rol administrador.

Las empresas son dadas de alta manualmente por el autor del sistema. No existe registro público ni autoservicio de alta.

---

### 2.1.7. Landing pública y formulario de contacto

La landing pública de Stay Sidekick es un sitio estático generado con **11ty** y plantillas **Nunjucks (njk)**. Esta decisión arquitectónica es deliberada: al tratarse de contenido completamente estático, no requiere ejecución de JavaScript en servidor ni funciones serverless; el HTML se genera en tiempo de compilación y se sirve directamente desde Nginx.

El formulario de contacto dirige la petición HTTP directamente al servidor Flask backend, donde se valida y procesa. No se utiliza ninguna solución de funciones serverless para este flujo. El comportamiento de la landing es independiente del panel Angular SPA y no comparte sesión ni estado con él.

---

## 2.2. Interfaz de usuario y experiencia de usuario

### 2.2.1. Principios de diseño y sistema visual

El sistema visual del panel está construido con **SASS** siguiendo la arquitectura **ITCSS** (Inverted Triangle CSS), organizada en ocho capas en orden estricto de especificidad creciente: Settings, Tools, Generic, Elements, Layout, Components, Utilities y Animations. Los nombres de clases siguen la metodología **BEM** (Block, Element, Modifier), garantizando que la especificidad de los selectores sea predecible y que los componentes sean independientes entre sí.

La tipografía utilizada es **Archivo** en formato variable font, lo que permite controlar el peso y la inclinación con una única fuente cargada. Los colores, tamaños de fuente, espaciados y breakpoints se definen como variables SASS en la capa Settings y se exponen como custom properties CSS en `:root`, permitiendo sobreescrituras puntuales sin romper el sistema.

El prototipado visual previo al desarrollo se realizó con **Figma**, donde se diseñaron los wireframes de las páginas principales y el sistema de componentes antes de traducirlos a código Angular.

### 2.2.2. Estructura de navegación

El panel Angular implementa una arquitectura SPA de página única con enrutamiento del lado del cliente. El layout principal se compone de un sidenav lateral retráctil y un área de contenido que renderiza la herramienta activa mediante `<router-outlet>`. Las rutas de herramientas se cargan de forma perezosa (*lazy load*) para reducir el bundle inicial.

Las rutas disponibles son: `/` (panel de bienvenida), `/mapa-calor`, `/notificaciones-checkin-tardio`, `/sincronizador-contactos`, `/maestro-apartamentos`, `/vault-comunicaciones` y `/perfil`. El acceso a cualquier ruta está protegido por un guard de autenticación que redirige al login si no hay token válido.

### 2.2.3. Flujos de usuario principales

El flujo tipo para el uso de cualquier herramienta sigue el mismo patrón: acceso al panel → selección de herramienta en el sidenav o menu principal → configuración de parámetros (fechas, fuente de datos, opciones) → generación del resultado → copia o descarga. La configuración persistente de la empresa (PMS, Google, IA) se gestiona desde una página de perfil separada, evitando que los ajustes estructurales interrumpan el flujo operativo diario.

El estado de cada componente de página se gestiona con señales (*signals*) y *computed values* de Angular, lo que garantiza reactividad sin necesidad de gestión de estado global.

### 2.2.4. Accesibilidad

El objetivo de accesibilidad del panel es el nivel **WCAG 2.1 AA**. Los criterios aplicados incluyen contraste de color suficiente entre texto y fondo, navegación completa por teclado, etiquetas descriptivas en todos los campos de formulario y mensajes de error asociados explícitamente a sus controles mediante atributos ARIA. La tipografía variable y el sistema de espaciado fluido contribuyen a la legibilidad en distintos tamaños de pantalla.

---

## 2.3. Usuarios objetivo y casos de uso

### 2.3.1. Perfiles de usuario

| Perfil | Rol en la empresa | Nivel técnico | Necesidades principales |
|---|---|---|---|
| **Recepcionista operativa** | Gestión diaria de reservas y coordinación de llegadas | Bajo — usuario habitual de PMS, no técnico | Acceso rápido a la información del día: check-ins tardíos, cuántas salidas hay mañana, mensajes listos para enviar sin redactar |
| **Coordinadora de limpieza** | Planificación de servicios de limpieza por apartamento | Bajo — no usa PMS directamente | Vista de carga por día para distribuir el equipo; no necesita datos nominales de huéspedes |
| **Propietario-gestor** | Propietario que gestiona directamente sus 5-20 propiedades | Medio — usa el PMS y herramientas de Google | Contactos sincronizados automáticamente, plantillas de bienvenida personalizadas, visión de ocupación por periodos |
| **Administrador de cuenta** | Responsable de la configuración de la plataforma en la empresa | Medio-alto | Alta del PMS, conexión con Google, gestión de plantillas corporativas, ajuste de parámetros por herramienta |

### 2.3.2. Casos de uso por herramienta

**CU-01 — Planificación de limpieza del lunes.**
Son las 09:00 del lunes. La coordinadora de limpieza abre el panel de Stay Sidekick, navega al mapa de calor y selecciona el rango de la semana en curso. En diez segundos obtiene una cuadrícula que muestra de un vistazo que el miércoles hay siete salidas y el viernes hay cuatro. Distribuye el equipo en consecuencia sin haber consultado el PMS.

**CU-02 — Detección de llegadas tardías en víspera de festivo.**
A las 16:00 del día anterior a un festivo, la recepcionista abre la herramienta de notificaciones. El sistema, con el PMS conectado, ha cargado automáticamente los check-ins del día siguiente y resalta los tres huéspedes con llegada después de las 20:00. La recepcionista selecciona la plantilla corporativa de llegada tardía, el sistema aplica el nombre del huésped y el nombre del apartamento, y obtiene tres mensajes independientes listos para pegar en WhatsApp.

**CU-03 — Sincronización de contactos tras el fin de semana.**
El propietario-gestor llega el lunes por la mañana y quiere tener en Google Contacts todos los huéspedes que han hecho check-in durante el fin de semana. Abre el sincronizador, selecciona el rango sábado-domingo y pulsa sincronizar. El sistema agrupa las reservas por huésped —uno de ellos tenía dos propiedades— y realiza el upsert en Google People API. En menos de un minuto los contactos están disponibles en el teléfono del gestor.

**CU-04 — Alta de nuevos apartamentos tras ampliar la cartera.**
La empresa acaba de incorporar cuatro nuevas propiedades al PMS. El administrador de cuenta accede a la herramienta del maestro de alojamientos, pulsa "Sincronizar con PMS" y el sistema extrae las propiedades activas de la cuenta y las inserta en el catálogo local. A partir de ese momento, las otras herramientas ya pueden enriquecer las reservas de esos apartamentos con su nombre y dirección.

**CU-05 — Personalización de plantilla para un mercado internacional.**
La empresa recibe un volumen creciente de huéspedes francófonos. El administrador accede al vault de comunicaciones, crea una nueva plantilla de bienvenida en español, la selecciona y pulsa "Traducir". El sistema invoca el servicio IA y devuelve el texto traducido al francés, que el administrador revisa, ajusta y guarda como plantilla independiente con idioma `fr`. A partir de ese momento, la recepcionista puede seleccionarla directamente desde las notificaciones de check-in tardío.

**CU-06 — Fallback sin PMS para empresa de nueva incorporación.**
Una empresa que acaba de integrarse en Stay Sidekick todavía no ha configurado el PMS porque su proveedor no dispone de API documentada. El administrador exporta las reservas de la semana desde el PMS en formato XLSX, sube el archivo al sincronizador de contactos y obtiene el CSV listo para importar en Google Contacts con las cabeceras exactas que la plataforma requiere. El flujo operativo es idéntico al del caso con PMS conectado, solo cambia el origen de los datos.