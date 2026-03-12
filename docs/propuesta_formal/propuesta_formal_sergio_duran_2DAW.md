# Propuesta de Proyecto Final - DAW 2º

**Autor:** Sergio Durán  
**Ciclo:** Desarrollo de Aplicaciones Web (DAW) - 2º año  
**Fecha de entrega:** 6 de marzo de 2026  
**Modalidad:** Individual  

---

## Índice

1. [Identificación de necesidades](#1-identificación-de-necesidades)
2. [Oportunidades de negocio](#2-oportunidades-de-negocio)
3. [Tipo de proyecto](#3-tipo-de-proyecto)
4. [Características específicas](#4-características-específicas)
5. [Obligaciones legales y prevención](#5-obligaciones-legales-y-prevención)
6. [Ayudas y subvenciones](#6-ayudas-y-subvenciones)
7. [Guión de trabajo](#7-guión-de-trabajo)
8. [Referencias](#8-referencias)

---

## 1. Identificación de necesidades

### Problema detectado

Durante mi experiencia laboral en el sector del alquiler vacacional (hasta noviembre de 2025), identifiqué que los Property Management Systems (PMS) como KrossBooking resuelven eficazmente la gestión central de reservas, canales y calendarios, pero **dejan sin cubrir tareas operativas diarias** que consumen tiempo significativo al equipo:

- **Coordinación de limpiezas**: Visualizar entradas/salidas por día y semana requiere abrir múltiples pestañas o exportar datos manualmente
- **Notificaciones de check-ins tardíos**: Detectar llegadas después de las 20:00h y generar comunicaciones personalizadas es un proceso manual repetitivo
- **Sincronización de contactos**: Mantener actualizada la agenda de Google Contacts con datos de huéspedes implica copiar y pegar información o importar CSV manualmente
- **Comunicaciones repetitivas**: Los mensajes operativos (instrucciones de acceso, protocolos, bienvenidas) están dispersos en las respuestas rápidas de WhatsApp de cada empleado, sin centralización ni versionado

Estas tareas no son el core del PMS, pero **ocupan entre 2-4 horas semanales** por empleado en equipos pequeños (2-5 personas).

### Cómo se detectó

- **Observación directa**: Trabajo como recepcionista en empresa de gestión de apartamentos vacacionales durante 2 años y 5 meses.
- **Análisis de flujos**: Identificación de tareas manuales repetitivas que no están automatizadas en el PMS utilizado (KrossBooking).
- **Validación con equipo**: Conversaciones con compañeros del departamento operativo y limpieza.

### Usuarios beneficiarios

- **Directos**: Equipos operativos de empresas de alquiler vacacional (recepcionistas, coordinadores de limpieza, propietarios que gestionan sus propios apartamentos).
- **Indirectos**: Huéspedes (mejor coordinación = mejor experiencia).

---

## 2. Oportunidades de negocio

### Análisis del mercado

**Soluciones existentes:**

- **PMS generalistas** (Guesty, Hostaway, Smoobu, Beds24): Cubren gestión de reservas, canales, calendarios y facturación, pero las herramientas operativas específicas son limitadas o inexistentes.
- **Herramientas especializadas aisladas**: Existen soluciones parciales (apps de limpieza como Properly, gestores de comunicaciones como Hospitable), pero requieren múltiples suscripciones y no están integradas entre sí.
- **Soluciones ad-hoc internas**: Muchas empresas crean hojas de cálculo o scripts propios, sin escalabilidad ni mantenimiento.

**Competencia directa identificada:** No existe una plataforma satélite multi-empresa que agrupe herramientas operativas específicas como capa complementaria al PMS o al menos realizan funciones parciales que se recogen en esta herramienta.

### Diferenciación

**Valor diferencial:**

- **No compite con el PMS**: Es una capa satélite que complementa, no sustituye.
- **Multi-empresa desde el diseño**: Motor de configuración parametrizable por empresa.
- **Agnóstica de PMS**: Arquitectura desacoplada, compatible con cualquier PMS mediante XLSX o API REST.
- **Enfoque en tareas operativas**: Resuelve el "trabajo invisible" que el PMS no cubre.

### Potencial

- **Usuarios potenciales**: Empresas de gestión de alquiler vacacional con 5 a 100 propiedades (nicho entre propietarios individuales y grandes operadores).
- **Escalabilidad**: Arquitectura multi-empresa permite añadir clientes sin modificar el código base.
- **Modelo de ingresos futuro**: Freemium (3 herramientas básicas gratuitas) + suscripción por herramientas adicionales.

---

## 3. Tipo de proyecto

### Tipo de aplicación

**Aplicación web híbrida:**

- **Parte estática (landing pública)**: Astro — generación estática, SEO optimizado, velocidad de carga.
- **Parte dinámica (panel de herramientas)**: Angular — SPA con gestión de estado, autenticación por empresa, interfaz reactiva.

### Justificación

- **SPA para el panel privado**: Las herramientas requieren interactividad en tiempo real (visualización de heatmaps, filtrado de reservas, sincronización con Google).
- **Landing estática**: La página pública no cambia frecuentemente; Astro optimiza carga y SEO.
- **Separación de contextos**: Landing para captación + panel privado para uso real.

### Arquitectura propuesta

**Cliente-servidor con backend RESTful desacoplado:**

```
┌─────────────────────┐
│   Frontend          │
│  Astro (landing)    │
│  Angular (panel)    │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│   Backend API       │
│   Flask (Python)    │
│   RESTful privada   │
└──────────┬──────────┘
           │
           ├─► PostgreSQL (BD interna)
           ├─► Google People API (OAuth 2.0)
           ├─► Google Gemini API (IA generación)
           └─► PMS externo (API REST o XLSX manual)
```

**Principios arquitectónicos:**

- **Backend agnóstico de PMS**: Capa de adaptadores para normalizar datos de diferentes PMS
- **API REST privada**: Solo consume el frontend propio, no es pública
- **Configuración por empresa**: Motor parametrizable en PostgreSQL (cada empresa activa/desactiva herramientas y define sus reglas)

---

## 4. Características específicas

### 4.1. Funcionalidades principales (MVP)

#### Herramienta 1: Mapa de calor de entradas/salidas

Visualización tipo heatmap de check-ins y check-outs por día/semana para coordinar limpiezas y gestonar turnos de recepción. La empresa configura qué rango de fechas.

**Entrada de datos:** API de PMS (Smoobu) o XLSX exportado manualmente como fallback.

---

#### Herramienta 2: Notificaciones automáticas para check-ins tardíos

Detecta reservas con llegada posterior a las 20:00h (parametrizable según el horario de trabajo de la empresa) y genera comunicaciones personalizadas según el protocolo interno. Configurable por empresa (hora límite, tipo de mensaje, idioma).

**Salida:** Mensaje listo para copiar y enviar por el canal que la empresa utilice (WhatsApp, email, SMS).

---

#### Herramienta 3: Sincronización con Google Contacts

Integración con Google People API (OAuth 2.0) para crear o actualizar automáticamente contactos en la agenda de Google de la empresa desde datos de reserva.

**Flujo:**

1. La empresa conecta su cuenta Google desde el panel (OAuth 2.0)
2. El sistema solicita permisos de lectura/escritura en contactos
3. Google gestiona la autenticación (incluido 2FA si la empresa lo tiene activado)
4. La aplicación guarda el refresh token encriptado en PostgreSQL
5. Al sincronizar, el backend procesa los datos de huéspedes en memoria y los sube a Google Contacts
6. El backend personaliza los contactos según configuración de la empresa:
   - Fecha de entrada ajustable al formato deseado (incluida en nombre o notas)
   - Nombre completo formateado según preferencia del usuario
   - Nombre del apartamento en notas o como etiqueta de grupo

**Fallback:** Exportación de CSV con cabeceras exactas de Google para importación manual desde `contacts.google.com` y de la misma forma, personalizable el cómo.

**RGPD:** Los datos de huéspedes no se persisten en base de datos más allá del procesamiento necesario.

---

#### Herramienta 4: Base de datos de alojamientos personalizada

Maestro de alojamientos gestionado por cada empresa dentro de la plataforma. La empresa introduce manualmente o importa desde XLSX los apartamentos que gestiona (ID único, nombre, dirección, ciudad). También se hidrata por requests a la API del PMS.

**Función:** Tabla de referencia para cruce de datos cuando se sube un fichero de reservas. El sistema enriquece automáticamente las reservas con nombre y dirección del alojamiento correspondiente.

---

#### Herramienta 5: Vault de comunicaciones y generador de mensajes asistido por IA

**Primera capa — Vault de plantillas:**

Biblioteca centralizada de plantillas de mensajes por empresa, almacenadas en PostgreSQL. Sustituye las respuestas rápidas dispersas en dispositivos personales del equipo.

Cada plantilla incluye campos variables (placeholders): `{NOMBRE}`, `{APARTAMENTO}`, `{HORA_LLEGADA}`, `{IDIOMA}`, `{PROTOCOLO_CHECKIN}`.

**Segunda capa — Generador asistido por IA:**

A partir de una plantilla seleccionada y los datos concretos de una reserva (esto último opcional), el backend Flask llama a un modelo de lenguaje para adaptar el texto.

**La IA NO inventa contenido desde cero**, sino que:

- Ajusta el tono (más formal o cercano) según configuración de la empresa.
- Traduce el mensaje al idioma del huésped.
- Genera pequeñas variaciones para evitar que todos los mensajes sean idénticos.

**Salida:** Mensaje final listo para copiar y enviar por el canal que la empresa utilice (correo, WhatsApp, SMS).

**BYOK (Bring Your Own Key):** Las empresas pueden configurar su propia API key de cualquier proveedor LLM compatible (Gemini, OpenAI, Claude). La clave se almacena encriptada en PostgreSQL. Por defecto, el sistema ofrece Gemini 2.0 Flash de forma gratuita (cuota compartida del proyecto).

---

### 4.2. Priorización de funcionalidades

- **Obligatorias en MVP**: Mapa de calor, Notificaciones check-ins tardíos, Sincronización Google Contacts, BD de alojamientos, Vault + generador IA
- **Trabajo futuro**: Integración directa con API de PMS adicionales, Contenido local asistido por IA (eventos, actividades), envio de los mensajes del vault gracias a la sincronización con los PMS.

---

### 4.3. Requisitos técnicos

#### 4.3.1. Stack tecnológico

**Frontend:**

- Angular 20 (panel dinámico)
- Astro 4 (landing estática)
- SASS con ITCSS y BEM
- Figma (wireframes)

**Backend:**

- Python 3.12 con Flask
- PostgreSQL 17
- `pandas`, `openpyxl` (procesamiento XLSX)
- `google-auth`, `google-api-python-client` (People API)
- `google-generativeai` (Gemini)
- `cryptography` (encriptación)

**Infraestructura:**

- Docker + Docker Compose
- Nginx (proxy inverso)
- GitHub Actions (CI/CD)
- Railway (despliegue)

**Integraciones externas:**

- Google People API (OAuth 2.0)
- Google Gemini 2.0 Flash (free tier)
- Smoobu API (desarrollo con 1 propiedad gratuita)

**Formulario de contacto:**

- Serverless (Railway Functions / Vercel Functions)
- Turnstile (Cloudflare) anti-spam

---

#### 4.3.2. Backend de lógica de negocio

API RESTful desacoplada de cualquier PMS concreto. Se gestiona la lógica interna de cada herramienta: procesamiento de datos, generación de mapas de calor, gestión de notificaciones programadas y autenticación con servicios externos. El diseño se pretende hacer modular para permitir activar o desactivar herramientas por empresa. La base de datos es mínima y, en caso de que sea necesario guardar datos sensibles, serán los menos sensibles (direcciones de apartamentos, nombres de los mismos) y tratados bajo las bases legales necesarias para su protección.

**Endpoints principales de la API REST:**

El backend expone una API REST interna, consumida exclusivamente por el frontend, con endpoints como:

- `GET /api/apartamentos`: devuelve el maestro de alojamientos de la empresa (id, nombre, dirección, ciudad).
- `GET /api/reservas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`: devuelve las reservas normalizadas para alimentar el mapa de calor, las notificaciones de check-in tardío y la sincronización de contactos.
- `POST /api/reservas/importar`: procesa un fichero XLSX/CSV de reservas subido manualmente, normaliza los datos y los devuelve en formato JSON para su uso inmediato en las herramientas.
- `POST /api/contactos/sincronizar`: a partir de un conjunto de reservas, sincroniza los contactos con Google People API (si está configurado OAuth) o genera un CSV compatible con Google Contacts como fallback.
- `GET /api/vault/plantillas` y `POST /api/vault/plantillas`: gestión de plantillas de comunicación por empresa (crear, editar, listar).
- `POST /api/vault/generar-mensaje`: genera un mensaje final a partir de una plantilla seleccionada y datos opcionales de contexto (reserva, destinatario), apoyándose en el módulo de IA cuando esté activo.
- `GET /api/vault/mensajes?reservaId=...`: consulta de mensajes generados asociados a una reserva o contexto concreto.
- `GET /api/pms/sincronizar`: llama internamente a la API del PMS configurado (Smoobu en el MVP), normaliza los datos recibidos y los guarda temporalmente para su uso por las herramientas.
- `GET /api/pms/status`: indica si la conexión con el PMS está activa o si se está trabajando únicamente con ficheros manuales.

Estos endpoints encapsulan la lógica de negocio de forma desacoplada de los PMS y de los servicios externos, manteniendo una interfaz estable para el frontend independientemente de los cambios en las integraciones.

---

#### 4.3.3. Gestión flexible de fuentes de datos

El backend está diseñado para trabajar con múltiples fuentes de datos de forma flexible, adaptándose a la configuración de cada empresa:

- Si la empresa tiene un PMS configurado (Smoobu en el MVP), los datos de reservas y apartamentos se obtienen directamente desde su API en tiempo real.
- Si la empresa mantiene un maestro de apartamentos en la base de datos (cargado previamente desde XLSX), este se utiliza como referencia para el cruce de datos con las reservas.
- Si no hay PMS configurado, el usuario puede subir un fichero XLSX de reservas de forma temporal (sin persistir en base de datos), y el sistema extraerá tanto las reservas como los apartamentos referenciados directamente del fichero para alimentar las herramientas en esa sesión.

**Lógica de prioridad en el backend:**

Cuando una herramienta solicita datos (por ejemplo, para notificaciones de check-in tardío), el backend sigue esta jerarquía:

1. **Reservas:** PMS conectado → XLSX temporal en sesión → error si no hay ninguna fuente.
2. **Apartamentos:** BBDD maestra → PMS conectado → XLSX temporal → error si no hay ninguna fuente.

De esta forma, si una empresa tiene PMS para reservas pero mantiene su lista de apartamentos manualmente en la base de datos (o viceversa), el sistema funciona sin problemas al combinar ambas fuentes. Si no hay PMS ni BBDD, el XLSX temporal debe contener toda la información necesaria para operar en esa sesión.

Esta arquitectura por capas permite que las herramientas funcionen independientemente de la fuente de datos disponible, garantizando compatibilidad universal sin acoplar la lógica de negocio a un proveedor o flujo concreto.

---

#### 4.3.4. Integración con servicios externos

El backend se integra con servicios de terceros para ampliar las capacidades del sistema sin duplicar infraestructura existente.

**Google People API y Google Contacts**

La herramienta de sincronización de contactos exporta datos de huéspedes a Google Contacts mediante OAuth 2.0 o, como fallback, genera un CSV compatible para importación manual. El backend personaliza los contactos según preferencias del usuario: formato de fecha de entrada, nombre completo ajustado y nombre del apartamento en notas o etiquetas.

**Smoobu API (y futuros PMS)**

El backend se conecta con Smoobu para obtener reservas y apartamentos en tiempo real. Incluye un módulo de normalización que convierte los datos recibidos desde cualquier PMS a un formato interno estándar, permitiendo que las herramientas funcionen independientemente del PMS conectado. Añadir soporte para un nuevo PMS solo requiere desarrollar un adaptador de normalización.

**IA para generación de mensajes**

La herramienta Vault integra asistencia de IA para adaptar mensajes desde las plantillas definidas por cada empresa: ajuste de tono, traducción a otros idiomas y generación de variaciones. La IA no crea contenido desde cero, trabaja sobre las plantillas existentes. Se ofrece Google Gemini 2.0 Flash (free tier) por defecto. Las empresas pueden configurar su propia API key de cualquier proveedor LLM compatible (Gemini, OpenAI, Claude) mediante BYOK, almacenándose encriptada en PostgreSQL.

**Visualización de mapas de calor**

El mapa de calor se genera en el frontend alimentado por datos del backend. Cada celda representa un día: número de entradas centrado arriba (verde, intensidad variable según volumen) y número de salidas centrado abajo (rojo, intensidad variable), separadas por una barra horizontal. Se utilizará una librería JavaScript si soporta este formato; si no, se construirá con HTML/CSS/JS personalizado.

---

#### 4.3.5. Base de datos

PostgreSQL centraliza el almacenamiento de datos mínimos necesarios para las herramientas, sin persistir información sensible de huéspedes (cumplimiento RGPD).

**Tablas principales:**

- `empresas`: autenticación, configuración de herramientas activas y API keys de PMS / IA (encriptadas).
- `usuarios`: id, empresa_id, email, rol, contraseña (bcrypt).
- `apartamentos`: ID único, nombre, dirección y ciudad. Se hidrata desde PMS si existe conexión, o mediante CRUD manual con importación XLSX como fallback.
- `plantillas_vault`: mensajes predefinidos por empresa, con CRUD completo en panel de control.
- `mensajes_generados`: registro de mensajes generados por IA asociados a reserva y plantilla.
- `configuracion_pms`: api_key encriptada, endpoint, estado de conexión activa.
- `logs_sincronizacion`: registro de accesos a APIs externas (empresa, fecha, origen, estado, nº registros).

No se almacena ningún dato personal de huéspedes en base de datos. Los datos de reservas se procesan en memoria durante la sesión y no se persisten.

---

### 4.4. Modelo y soporte a empresas

El proyecto se publica bajo licencia privada. Durante el desarrollo del MVP (hasta el 15 de mayo de 2026), las empresas participantes reciben:

- Alta manual y acceso gratuito a las herramientas activas.
- Posibilidad de solicitar nuevas herramientas fuera del formulario.
- Soporte durante el desarrollo y 6 meses después.

Como contrapartida, las empresas participantes son reconocidas en la landing pública mientras el proyecto esté operativo.

---

### 4.5. Conexiones con PMS y análisis del sector

La arquitectura del proyecto está diseñada para ser agnóstica del PMS utilizado por cada empresa. La integración con sistemas externos queda planificada como línea de trabajo futuro tras el MVP, priorizando los PMS con API REST pública y documentada más relevantes del mercado.

| PMS | API REST | Documentación | Plan gratuito/trial | Notas |
|-----|----------|---------------|---------------------|-------|
| Smoobu | ✅ Pública | ⭐⭐⭐⭐ | ✅ Gratuito (1 prop) | Ideal desarrollo |
| Beds24 | ✅ OpenAPI | ⭐⭐⭐⭐⭐ | ✅ Plan gratuito | Muy documentado |
| Hostaway | ✅ Pública | ⭐⭐⭐⭐⭐ | ⚠️ Demo petición | API madura |
| Guesty | ✅ Pública | ⭐⭐⭐⭐⭐ | ❌ Pago | Enterprise |
| Cloudbeds | ✅ Pública | ⭐⭐⭐⭐ | ⚠️ Trial 14d | Suficiente demo |
| KrossBooking | ❌ No oficial | ⭐ krossApy (scraping) | N/A | Contacto directo |

Durante el desarrollo del MVP, la entrada de datos se gestiona con ficheros XLSX autogenerados por el PMS para garantizar compatibilidad universal. Todos los PMS listados soportan exportación nativa; el objetivo es parametrizar la posición de los datos según el formato de cada exportación.

---

## 5. Obligaciones legales y prevención

### Normativa aplicable

#### RGPD (Reglamento General de Protección de Datos)

**Datos tratados:**

- **Empresas (clientes):** Email, nombre comercial, ciudad, configuración → base legal: ejecución de contrato
- **Huéspedes (datos de terceros):** Nombre, teléfono, email, fechas → base legal: interés legítimo (gestión operativa)

**Principios aplicados:**

- **Minimización**: Solo datos mínimos necesarios; datos de huéspedes **no se persisten**, solo se procesan en memoria
- **Limitación de finalidad**: Uso exclusivo para herramientas solicitadas, no marketing ni cesión
- **Seguridad**: Tokens OAuth y API keys **encriptados** (Fernet), HTTPS obligatorio
- **Transparencia**: Documentación clara en landing sobre datos procesados

**Responsabilidades:**

- **Responsable del tratamiento:** Cada empresa cliente
- **Encargado del tratamiento:** Este proyecto
- **Acuerdo de encargo:** Documento a firmar con cada empresa

#### LSSI-CE (Ley de Servicios de la Sociedad de la Información)

- **Aviso legal**: Identificación del titular, NIF, domicilio, contacto
- **Política de privacidad**: Datos tratados, finalidad, derechos ARCO
- **Política de cookies**: Información y consentimiento si se usan cookies

---

### Medidas de seguridad

- **Encriptación de credenciales**: Tokens OAuth y API keys encriptados con `cryptography` (Fernet)
- **Autenticación por empresa**: Login con bcrypt, sesiones JWT
- **OAuth 2.0 delegado**: Google gestiona autenticación (incluye 2FA)
- **HTTPS obligatorio**: SSL/TLS en Railway, Nginx proxy
- **Validación anti-spam**: Turnstile en formulario contacto
- **Protección CSRF**: Tokens CSRF en formularios
- **No persistencia datos sensibles**: Huéspedes procesados en memoria, no en BD
- **Logs auditables**: Registro de accesos a APIs externas

---

### Accesibilidad web (WCAG)

**Nivel objetivo:** WCAG 2.1 nivel AA

**Medidas previstas:**

- **Perceptible**: Contraste 4.5:1, alternativas textuales, subtítulos en videos
- **Operable**: Navegación por teclado, foco visible, sin trampas
- **Comprensible**: Etiquetas claras, mensajes de error descriptivos
- **Robusto**: HTML semántico, ARIA labels, compatible con lectores de pantalla

**Herramientas de validación:** Lighthouse, WAVE, axe DevTools y auditorias TAWDIS

---

## 6. Ayudas y subvenciones

### Ayudas disponibles (España, 2026)

#### Kit Digital (Red.es)

**Descripción:** Ayudas para digitalización de pymes y autónomos.

**Segmento aplicable:** Soluciones de Gestión de Clientes (hasta 2.000€).

**Requisitos:** Empresa dada de alta, <50 empleados, facturación <10M€.

**Aplicabilidad:** El proyecto podría ofrecerse como solución subvencionable para empresas turísticas.

---

#### ENISA (Línea Emprendedores)

**Descripción:** Préstamos participativos 25.000€-75.000€, sin garantías.

**Aplicabilidad:** Si se constituye como startup tras el TFG.

---

#### Programa Minerva (Junta de Andalucía)

**Descripción:** Ayudas transformación digital en Andalucía.

**Aplicabilidad:** Colaboración con empresas andaluzas del sector turístico.

---

### Recursos gratuitos utilizados

- **Vercel/Netlify**: Free tier (landing Astro)
- **Google Gemini API**: Free tier 500 req/día
- **Google People API**: Gratuita
- **Smoobu API**: Plan gratuito 1 propiedad
- **GitHub Actions**: Gratuito (repos públicos)
- **Cloudflare Turnstile**: Gratuito
- **Figma**: Free tier

**Coste operativo del MVP:** 0€ durante desarrollo.

---

## 7. Guión de trabajo

### Cronograma general

La entrega está programada para más adelante, pero mi fecha límite para el desarrollo y soluciones de errores, es hasta el 15 de Mayo, principalmente de cara las empresas.

**Periodo:** 6 marzo - 15 mayo 2026 (10 semanas)

| Fase | Duración | Semanas | Hitos |
|------|----------|---------|-------|
| Análisis y diseño | 2 sem | 1-2 | Wireframes, modelo BD, diseño API |
| Sprint 1: Infraestructura | 1 sem | 3 | Docker, CI/CD, Railway, PostgreSQL |
| Sprint 2: Herramientas 1-2 | 2 sem | 4-5 | Mapa calor + Notificaciones |
| Sprint 3: Herramienta 3 | 2 sem | 6-7 | OAuth Google + People API |
| Sprint 4: Herramientas 4-5 | 2 sem | 8-9 | BD alojamientos + Vault + IA |
| Sprint 5: Landing + Demo | 1 sem | 10 | Landing Astro, capturas, docs |

---

### Fases detalladas

### Cronograma general

**Periodo:** 6 marzo - 28 mayo 2026 (12 semanas, 12 sprints de 1 semana).

| Fase / Sprint | Duración | Semanas internas | Hitos |
| :-- | :-- | :-- | :-- |
| Análisis y diseño inicial | 2 sem | 1-2 | Flujos, wireframes, modelo BD, diseño API |
| Sprint 1: Entorno y cuentas | 1 sem | 3 | Repositorios, GitHub Projects, APIs y claves creadas |
| Sprint 2: Wireframes y UX | 1 sem | 4 | Flujos de usuario y wireframes validados |
| Sprint 3: Mockup y sistema de diseño | 1 sem | 5 | Mockup navegable y decisiones de diseño cerradas |
| Sprint 4: Infraestructura | 1 sem | 6 | Docker, CI/CD, Railway, PostgreSQL operativos |
| Sprint 5: Landing + serverless | 1 sem | 7 | Landing Astro, función serverless y Turnstile |
| Sprint 6: Herramienta 1 | 1 sem | 8 | Mapa de calor funcional con datos de prueba |
| Sprint 7: Herramienta 2 | 1 sem | 9 | Notificaciones check‑ins tardíos funcionales |
| Sprint 8: Herramienta 3 | 1 sem | 10 | Sincronización Google Contacts (OAuth + CSV) |
| Sprint 9: Herramienta 4 | 1 sem | 11 | BD de alojamientos integrada con reservas |
| Sprint 10: Herramienta 5 | 1 sem | 12 | Vault de plantillas + generador IA funcional |
| Sprint 11: Pulido MVP + memoria | 1 sem | 13 | Refactor, pruebas y borrador de memoria TFG |
| Sprint 12: Preparación defensa | 1 sem | 14 | Presentación, guion y ensayos de la defensa |

***

### Sprints detallados

#### Sprint 1 (6–12 marzo): Propuesta, análisis y configuración

**Tareas:**

- Cierre y entrega de la propuesta formal del proyecto.
- Análisis comparativo rápido de frameworks y validación del stack elegido.
- Creación de repositorios en GitHub, configuración básica de ramas y GitHub Projects.
- Alta de cuentas y obtención de API keys mínimas (Gemini, Smoobu, Google Cloud).

**Entregables:**

- Propuesta de TFG entregada.
- Repositorios iniciales con README y tablero de GitHub Projects enlazado.
- Vídeo corto de sprint review explicando arquitectura y decisiones iniciales.

***

#### Sprint 2 (13–19 marzo): Flujos de usuario y wireframes

**Tareas:**

- Definición de flujos de usuario para cada herramienta (1 a 5).
- Creación de wireframes low‑fi en Figma para landing y panel.
- Revisión de flujos con 1–2 usuarios reales del sector y ajustes.

**Entregables:**

- Enlace a Figma con wireframes navegables.
- Documento breve con conclusiones de las pruebas de flujo.

***

#### Sprint 3 (20–26 marzo): Mockup y decisiones de diseño

**Tareas:**

- Creación de moodboard y sistema básico de diseño (tipografía, color, componentes).
- Conversión de wireframes a mockups high‑fi siguiendo diseño atómico.
- Definición de componentes clave que se reutilizarán en Angular y Astro.

**Entregables:**

- Mockup navegable en Figma.
- Documento de decisiones de diseño (paleta, componentes, espaciados).

***

#### Sprint 4 (27 marzo – 2 abril): Infraestructura y backend base

**Tareas:**

- Configuración de Docker y Docker Compose para backend y base de datos.
- Despliegue inicial del backend Flask y PostgreSQL en Railway.
- Configuración de Nginx como proxy inverso (local o remoto según requisitos).
- Pipeline básico de CI/CD con GitHub Actions (tests y despliegue automático a main).

**Entregables:**

- Backend accesible en un entorno remoto de pruebas.
- Pipeline de CI/CD funcionando con al menos un test de smoke.

***

#### Sprint 5 (3–9 abril): Landing Astro y formulario serverless

**Tareas:**

- Creación de la estructura ITCSS y BEM para estilos globales.
- Maquetación de la primera versión de la landing en Astro, conectada con el diseño.
- Implementación y despliegue de función serverless (Railway/Vercel) para el formulario de contacto.
- Integración de Cloudflare Turnstile y prueba de recepción de mensajes (por ejemplo, en Discord o email).

**Entregables:**

- Landing desplegada en entorno público.
- Vídeo mostrando envío de formulario y recepción del mensaje.
- Documentación de la arquitectura de la parte pública.

***

#### Sprint 6 (10–16 abril): Herramienta 1 — mapa de calor

**Tareas:**

- Modelado de la estructura de datos de reservas normalizadas en el backend.
- Endpoints para importar XLSX/CSV y para obtener reservas agregadas por día.
- Implementación de la visualización del mapa de calor en Angular (librería o componente propio).
- Pruebas con datos reales o sintéticos exportados desde un PMS.

**Entregables:**

- Demo funcional del mapa de calor navegable desde el panel.
- Documento con formato esperado de ficheros XLSX y ejemplos.

***

#### Sprint 7 (17–23 abril): Herramienta 2 — notificaciones de check‑in tardío

**Tareas:**

- Lógica de detección de reservas con llegada posterior a la hora configurada por empresa.
- Pantalla Angular para listar reservas afectadas y previsualizar notificaciones.
- Endpoint para generar el texto base del mensaje según protocolo interno.
- Tests básicos de borde (zonas horarias, horas límite distintas por empresa).

**Entregables:**

- Demo de la herramienta 2 integrada en el panel.
- Documento de parametrización de horarios y reglas de notificación.

***

#### Sprint 8 (24–30 abril): Herramienta 3 — sincronización Google Contacts

**Tareas:**

- Implementación de flujo OAuth 2.0 con Google People API.
- Gestión de tokens (almacenamiento encriptado en PostgreSQL).
- Endpoint para sincronizar contactos y opción de exportar CSV compatible con Google Contacts.
- Pantalla de configuración en el panel para conectar/desconectar la cuenta Google.

**Entregables:**

- Sincronización real con una cuenta de prueba de Google Contacts.
- Vídeo corto mostrando el flujo completo de conexión y sincronización.

***

#### Sprint 9 (1–7 mayo): Herramienta 4 — base de datos de alojamientos

**Tareas:**

- Diseño y creación de la tabla `apartamentos` y endpoints CRUD.
- Importación de alojamientos desde XLSX, con validaciones básicas.
- Integración del maestro de alojamientos con las herramientas 1 y 2 (enriquecimiento de reservas).
- UI en Angular para gestionar alojamientos (listado, alta, edición, borrado).

**Entregables:**

- Maestro de alojamientos funcional en el panel.
- Documento que describe la lógica de prioridad de fuentes de datos (PMS, BD, XLSX).

***

#### Sprint 10 (8–14 mayo): Herramienta 5 — Vault de comunicaciones e IA

**Tareas:**

- Implementación de la tabla `plantillas_vault` y endpoints CRUD.
- Pantalla en Angular para gestionar plantillas por empresa con placeholders.
- Integración con proveedor LLM (Gemini 2.0 Flash por defecto, BYOK opcional).
- Endpoint `POST /api/vault/generar-mensaje` que reciba plantilla + datos de reserva y devuelva mensaje final.

**Entregables:**

- Generador funcional de mensajes asistidos por IA integrado en el panel.
- Documentación de uso del Vault y ejemplos de plantillas.

***

#### Sprint 11 (15–21 mayo): Pulido del MVP y memoria del TFG

**Tareas:**

- Refactor de código backend y frontend, mejora de nombres, módulos y tests.
- Pruebas end‑to‑end mínimas sobre los flujos críticos (importar reservas, mapa de calor, notificaciones, contactos, Vault).
- Revisión de requisitos legales (RGPD, LSSI‑CE, WCAG) y comprobación básica con herramientas de accesibilidad.
- Redacción de la memoria del TFG: introducción, estado del arte, análisis, diseño, implementación, pruebas y conclusiones.

**Entregables:**

- MVP estable, desplegado y accesible.
- Borrador avanzado de la memoria del TFG listo para revisión.

***

#### Sprint 12 (22–28 mayo): Preparación y ensayo de la presentación del TFG

**Tareas:**

- Preparación de las diapositivas de la defensa (problema, solución, arquitectura, demo, conclusiones).
- Elaboración del guion de la presentación oral, con tiempos por sección.
- Ensayos de la defensa grabados (al menos 2), revisión de tiempo y mensajes clave.
- Revisión final de la memoria, corrección de erratas y generación de versión definitiva en PDF.

**Entregables:**

- Presentación (diapositivas) finalizada y lista para exponer.
- Guion detallado de la defensa y enlace a vídeos de ensayo (uso personal).
- Memoria definitiva generada y lista para entrega en los plazos del centro.

***

### Hitos y entregas intermedias

| Fecha (2026) | Hito | Entregable |
| :-- | :-- | :-- |
| 12 marzo | Propuesta y análisis inicial cerrados | Propuesta TFG entregada, repositorios creados, cuentas y API keys configuradas |
| 19 marzo | UX definida | Flujos de usuario y wireframes en Figma validados con al menos un usuario del sector |
| 26 marzo | Diseño visual cerrado | Mockup navegable, documento de decisiones de diseño (tipografía, colores, componentes) |
| 2 abril | Infraestructura desplegada | Backend Flask y PostgreSQL en Railway, Docker y CI/CD básicos funcionando |
| 9 abril | Landing funcional | Landing en Astro desplegada, formulario serverless con Turnstile y prueba de recepción correcta |
| 16 abril | Herramienta 1 operativa | Mapa de calor navegable en el panel con datos de ejemplo (XLSX/CSV) |
| 23 abril | Herramienta 2 operativa | Pantalla de notificaciones de check‑in tardío funcionando con reglas configurables |
| 30 abril | Integración Google Contacts | Flujo OAuth completado, sincronización real con Google Contacts y exportación CSV |
| 7 mayo | Maestro de alojamientos | CRUD de alojamientos integrado con reservas y lógica de prioridad de fuentes documentada |
| 14 mayo | Vault + IA completo | Gestión de plantillas y generación de mensajes asistidos por IA funcionando de extremo a extremo |
| 21 mayo | MVP estable + memoria avanzada | MVP desplegado, pruebas básicas pasadas y borrador de memoria listo para revisión |
| 28 mayo | Materiales de defensa listos | Presentación, guion de defensa y versión final de memoria preparados para entrega |

---

### Herramientas de gestión

- **GitHub Projects**: Tablero Kanban (Backlog, In Progress, In Review, Done)
- **Toggl Track**: Registro de horas por tarea
- **GitHub Actions**: CI/CD automatizado
- **Figma**: Wireframes y sistema de diseño

---

## 8. Referencias

### Documentación técnica

- Flask: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- Angular: [https://angular.dev/](https://angular.dev/)
- Astro: [https://docs.astro.build/](https://docs.astro.build/)
- PostgreSQL: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
- Google People API: [https://developers.google.com/people](https://developers.google.com/people)
- Google Gemini API: [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
- Smoobu API: [https://docs.smoobu.com/](https://docs.smoobu.com/)

### Normativa

- RGPD: [https://www.boe.es/doue/2016/119/L00001-00088.pdf](https://www.boe.es/doue/2016/119/L00001-00088.pdf)
- LSSI-CE: [https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758](https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758)
- WCAG 2.1: [https://www.w3.org/TR/WCAG21/](https://www.w3.org/TR/WCAG21/)

### Ayudas

- Kit Digital: [https://www.red.es/es/iniciativas/kit-digital](https://www.red.es/es/iniciativas/kit-digital)
- ENISA: [https://www.enisa.es/](https://www.enisa.es/)
- Programa Minerva: [https://www.juntadeandalucia.es/](https://www.juntadeandalucia.es/)

---

**Fin de la propuesta**
