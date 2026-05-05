## 1. Origen de la idea y motivación del proyecto

La idea nace de la experiencia directa como recepcionista en una empresa gestora de apartamentos turísticos durante **2 años y 5 meses**. A lo largo de ese tiempo quedó patente que determinadas tareas operativas cotidianas —repetitivas, manuales y fragmentadas entre herramientas— consumían un tiempo desproporcionado que restaba capacidad para atender reservas activas, mejorar la experiencia del huésped o coordinar al equipo de forma eficiente.

Este problema no era exclusivo del puesto de recepción: afectaba a los compañeros en rotación, que expresaban las mismas fricciones de forma recurrente. Bajo esas observaciones y quejas compartidas se desarrolló un primer boceto funcional en **Java con JavaFX** como interfaz gráfica: una herramienta sencilla que cruzaba información introducida manualmente para facilitar el envío de un correo y generar contactos rápidamente.

Con mayor formación técnica, se desplegó un segundo prototipo sobre el stack **MERN** (MongoDB, Express, React, Node.js), ampliando las funcionalidades con un mapa de calor y permitiendo la subida de ficheros `.csv` para la persistencia y cruce de datos. Este prototipo, en su versión más básica —sin sesiones ni autenticación por empresa—, **sigue en uso a día de hoy**, lo que valida empíricamente que la herramienta resuelve necesidades reales y abre la puerta a su venta y escalado a otras empresas del sector.

El proyecto **Stay Sidekick** nace de esa evolución. No pretende competir con los PMS (*Property Management Systems*) modernos del mercado, sino ocupar los huecos operativos que esos sistemas no cubren o cubren de forma poco práctica. Es una capa satélite: complementa al PMS sin sustituirlo.

---

## 1.1. Expectativas y objetivos específicos

El objetivo principal es diseñar, desarrollar y desplegar una plataforma web multi-empresa que automatice las tareas operativas más comunes del sector del alquiler vacacional, ofreciendo herramientas satélite configurables por empresa como complemento directo al PMS utilizado.

### Objetivos específicos

- **Desarrollar un motor de configuración parametrizable por empresa**, de modo que cada herramienta se adapte a los formatos de datos, protocolos internos y preferencias de cada cliente, sin modificar el código base.
- **Implementar las cinco herramientas del MVP**: mapa de calor de entradas y salidas, notificaciones automáticas para check-ins tardíos, sincronización con Google Contacts, base de datos de alojamientos y vault de comunicaciones con generador asistido por IA.
- **Garantizar compatibilidad universal con cualquier PMS**, mediante entrada de datos por ficheros XLSX autogenerados como fallback e integración vía API REST cuando sea posible (Smoobu como PMS de referencia en el MVP).
- **Construir una arquitectura multi-tenant real**, con autenticación por empresa, catálogo personalizado y configuración persistente por cuenta.
- **Cumplir con la normativa aplicable** (RGPD, LSSI-CE, WCAG 2.1 AA), garantizando que los datos personales de huéspedes se tratan únicamente en memoria y no se persisten en base de datos.
- **Desplegar el MVP en producción** con infraestructura real (Docker, Nginx, Railway, GitHub Actions CI/CD) antes del 15 de mayo de 2026, con al menos una empresa del sector como caso de uso activo.
- **Documentar el proyecto de forma completa**: memoria técnica, wireframes en Figma, vídeo de demostración y presentación de defensa.

### Expectativas a futuro

Más allá del alcance del TFG, Stay Sidekick tiene proyección comercial como producto bajo licencia privada. Las empresas participantes durante el desarrollo recibirán acceso gratuito y soporte directo. A largo plazo se contempla un modelo *freemium* (herramientas básicas gratuitas, herramientas adicionales por suscripción) con reconocimiento permanente en la landing pública para las empresas fundadoras.

---

## 1.2. Análisis comparativo de aplicaciones similares

El mercado de gestión de alquiler vacacional cuenta con soluciones consolidadas, pero ninguna cubre de forma directa, práctica y configurable las necesidades operativas que Stay Sidekick aborda.

### Panorama actual

Las soluciones existentes se dividen en dos categorías principales:

- **PMS generalistas** (Smoobu, Beds24, KrossBooking, Guesty, Hostaway): resuelven eficazmente la gestión de reservas, canales, calendarios y facturación, pero sus herramientas operativas específicas son limitadas o inexistentes. Sus paneles están orientados a la gestión centralizada, no a la coordinación del equipo operativo en el terreno.
- **Herramientas especializadas aisladas** (Properly para limpiezas, Hospitable para mensajería): cubren parcialmente alguna necesidad concreta, pero requieren múltiples suscripciones independientes y no están integradas entre sí.

### Análisis de competidores directos identificados

**Smoobu** es uno de los PMS más extendidos entre medianas empresas del sector en España y Europa. Ofrece API REST bien documentada con plan gratuito para una propiedad, lo que lo convierte en el PMS de referencia del MVP. Sin embargo, no ofrece visualizaciones tipo heatmap, las automatizaciones de mensajería son genéricas y no existe integración con Google Contacts.

**Beds24** destaca por su sistema de automatizaciones mediante triggers y su API OpenAPI. Es técnicamente potente, pero con una curva de aprendizaje elevada que lo hace inaccesible para equipos pequeños sin perfil técnico. Está incluido en la hoja de ruta de Stay Sidekick como segundo PMS a integrar tras el MVP. Tampoco cubre las funcionalidades operativas específicas que aborda este proyecto.

**KrossBooking** es el PMS del entorno laboral del que nació el proyecto. No dispone de API pública oficial, y el acceso externo depende de soluciones no oficiales. Esto lo sitúa como objetivo de integración futura condicionada a acuerdo con una empresa del sector, dejando Smoobu como primera integración API del MVP.

### Tabla comparativa funcional

| Herramienta | Mapa de calor operativo | Notificaciones configurables | Sincronización Google Contacts | Vault de comunicaciones | Configurable por empresa |
| --- | --- | --- | --- | --- | --- |
| Smoobu | ❌ | ⚠️ Básicas | ❌ | ⚠️ Limitado | ❌ |
| Beds24 | ❌ | ⚠️ Complejas | ❌ | ⚠️ Templates email | ⚠️ Parcial |
| KrossBooking | ❌ | ⚠️ Estándar | ❌ | ⚠️ Mínimo | ❌ |
| Hospitable | ❌ | ✅ Avanzadas | ❌ | ✅ Con variables | ⚠️ Parcial |
| Properly | ⚠️ Vista de tareas | ❌ | ❌ | ❌ | ❌ |
| **Stay Sidekick** | **✅ Heatmap configurable** | **✅ Por empresa y protocolo** | **✅ API + CSV fallback** | **✅ Con IA (BYOK)** | **✅ Motor propio** |

### Posicionamiento

No existe actualmente una plataforma satélite multi-empresa que agrupe herramientas operativas específicas como capa complementaria al PMS, que sea completamente configurable por empresa sin tocar código y que ofrezca las cinco funcionalidades del MVP en un único producto integrado. Stay Sidekick se posiciona en ese hueco del mercado, entre las necesidades que los PMS no resuelven y las soluciones especializadas que sólo cubren una parte del problema.