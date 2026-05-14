# 01-introduccion

---

## Indice

- [1.1. Origen de la idea y motivacion del proyecto](#11-origen-de-la-idea-y-motivacion-del-proyecto)
- [1.2. Expectativas y objetivos especificos](#12-expectativas-y-objetivos-especificos)
	- [Objetivo general](#objetivo-general)
	- [Objetivos especificos](#objetivos-especificos)
	- [Expectativas a futuro](#expectativas-a-futuro)
- [1.3. Analisis comparativo de aplicaciones similares](#13-analisis-comparativo-de-aplicaciones-similares)
	- [Panorama actual](#panorama-actual)
	- [Analisis de competidores directos](#analisis-de-competidores-directos)
	- [Tabla comparativa funcional](#tabla-comparativa-funcional)
	- [Posicionamiento](#posicionamiento)

## 1.1. Origen de la idea y motivacion del proyecto

La idea de Stay Sidekick surge de una experiencia profesional directa como recepcionista en una empresa gestora de apartamentos turisticos durante **2 años y 5 meses**. En ese periodo se detecto que una parte importante de la jornada se destinaba a tareas repetitivas, manuales y distribuidas en varias herramientas, lo que reducia la capacidad para atender reservas activas, mejorar la experiencia del huesped y coordinar al equipo.

La problematica no afectaba solo a un puesto concreto: era una friccion compartida por distintos companeros en rotacion. A partir de estas observaciones se creo un primer boceto funcional en **Java con JavaFX**, orientado a cruzar datos introducidos manualmente para agilizar envios de correo y generacion de contactos.

Con una base tecnica mas solida se desarrollo un segundo prototipo sobre stack **MERN** (MongoDB, Express, React, Node.js). Esta version incorporo nuevas capacidades, como el mapa de calor y la carga de archivos `.csv` para persistencia y cruce de datos. Aunque era una version basica, sin sesiones ni autenticacion por empresa, **sigue en uso actualmente**, lo que confirma su utilidad real y su potencial de escalado.

Stay Sidekick nace como evolucion de ese recorrido. No busca sustituir a los PMS (*Property Management Systems*) existentes, sino cubrir necesidades operativas que estos sistemas no resuelven de forma suficiente. Su enfoque es el de una capa satelite: complementa al PMS y se adapta a la operativa diaria de cada empresa.

---

## 1.2. Expectativas y objetivos especificos

### Objetivo general

Disenar, desarrollar y desplegar una plataforma web multiempresa que automatice tareas operativas frecuentes del alquiler vacacional mediante herramientas satelite configurables por cuenta, como complemento directo al PMS.

### Objetivos especificos

- **Desarrollar un motor de configuracion parametrizable por empresa**, para adaptar cada herramienta a formatos de datos, protocolos internos y preferencias de cliente sin modificar el codigo base.
- **Implementar las cinco herramientas del MVP**: mapa de calor de entradas y salidas, notificaciones de check-in tardio, sincronizacion con Google Contacts, base de datos de alojamientos y vault de comunicaciones asistido por IA.
- **Garantizar compatibilidad con distintos PMS**, mediante integracion API REST cuando exista y mediante importacion XLSX como mecanismo de respaldo.
- **Construir una arquitectura multi-tenant real**, con autenticacion por empresa, catalogo personalizado y configuracion persistente por cuenta.
- **Cumplir normativa aplicable** (RGPD, LSSI-CE y WCAG 2.1 AA), priorizando minimizacion y tratamiento responsable de datos.
- **Desplegar el MVP en produccion** con infraestructura real (Docker, Nginx, Railway y GitHub Actions CI/CD), con al menos un caso de uso empresarial activo.
- **Documentar el proyecto de forma completa**, incluyendo memoria tecnica, wireframes, demostracion y defensa.

### Expectativas a futuro

Mas alla del alcance del TFG, Stay Sidekick se plantea con proyeccion comercial como producto bajo licencia privada. Las empresas que colaboren en etapas iniciales dispondran de acceso y soporte directo. A medio plazo se contempla un modelo *freemium*, con funcionalidades base gratuitas y herramientas avanzadas bajo suscripcion.

---

## 1.3. Analisis comparativo de aplicaciones similares

El mercado de gestion de alquiler vacacional dispone de soluciones consolidadas, pero ninguna cubre de forma integrada, configurable y enfocada a operativa diaria el conjunto de necesidades que aborda Stay Sidekick.

### Panorama actual

Las soluciones existentes se agrupan en dos bloques:

- **PMS generalistas** (Smoobu, Beds24, KrossBooking, Guesty, Hostaway): resuelven reservas, canales, calendarios y facturacion, pero suelen ofrecer soporte limitado para tareas operativas concretas del dia a dia.
- **Herramientas especializadas aisladas** (Properly, Hospitable): cubren necesidades puntuales, pero obligan a gestionar varias suscripciones y no siempre comparten un flujo unificado.

### Analisis de competidores directos

**Smoobu**

Es uno de los PMS mas extendidos en pymes del sector y ofrece API REST documentada con plan de entrada asequible. Por ello se adopta como PMS de referencia en el MVP. Como limitacion, no incorpora de forma nativa un mapa de calor operativo, ni sincronizacion directa con Google Contacts, ni un vault configurable orientado a protocolos internos.

**Beds24**

Destaca por su capacidad de automatizacion y por su API OpenAPI. No obstante, su curva de aprendizaje suele ser elevada para equipos sin perfil tecnico. Se considera objetivo de integracion posterior al MVP.

**KrossBooking**

Fue el PMS del entorno donde surge el proyecto, pero no dispone de API publica oficial en condiciones equivalentes a otros proveedores. Su integracion se plantea como linea futura sujeta a acuerdos especificos.

### Tabla comparativa funcional

| Herramienta | Mapa de calor operativo | Notificaciones configurables | Sincronizacion Google Contacts | Vault de comunicaciones | Configurable por empresa |
| --- | --- | --- | --- | --- | --- |
| Smoobu | No | Basico | No | Limitado | No |
| Beds24 | No | Avanzado pero complejo | No | Parcial | Parcial |
| KrossBooking | No | Estandar | No | Minimo | No |
| Hospitable | No | Avanzado | No | Con variables | Parcial |
| Properly | Parcial (tareas) | No | No | No | No |
| **Stay Sidekick** | **Si** | **Si, por empresa y protocolo** | **Si** | **Si, con IA opcional** | **Si** |

### Posicionamiento

Stay Sidekick se posiciona como una capa operativa satelite para empresas de alquiler vacacional que ya trabajan con PMS, pero necesitan resolver procesos concretos con mas flexibilidad. Su diferencial es combinar, en una misma plataforma, configuracion por empresa, enfoque multi-tenant y un conjunto de herramientas operativas integradas que normalmente aparecen dispersas o no disponibles en los sistemas tradicionales.