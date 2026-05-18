# Seguridad

## Alcance

Este documento aplica al repositorio de Stay Sidekick, a su backend Flask, al frontend Angular, al sitio web 11ty y al despliegue publicado mediante nginx en Railway.

Su objetivo es fijar un canal de reporte responsable y dejar por escrito que controles de seguridad existen hoy en el proyecto. No sustituye a la documentacion tecnica de arquitectura, despliegue ni desarrollo.

## Como reportar una vulnerabilidad

El mecanismo preferente actual es el formulario de contacto disponible en el despliegue publico de Stay Sidekick. En el mensaje indica claramente que se trata de un reporte de seguridad y facilita, como minimo:

- resumen del problema y posible impacto
- ruta o modulo afectado
- condiciones para reproducirlo
- evidencia suficiente para validar el fallo sin publicar un exploit completo
- un medio de respuesta para continuar la coordinacion

No publiques secretos, tokens, cookies, volcados de base de datos, datos personales ni detalles de explotacion en issues, pull requests, discussions o comentarios publicos del repositorio.

Si necesitas avisar de que existe un problema pero todavia no puedes compartir detalles de forma privada, limita el mensaje publico a una notificacion neutra y pide continuacion por canal privado.

## Expectativas de respuesta

Stay Sidekick no mantiene, por ahora, un equipo de seguridad separado del mantenimiento general del proyecto. Aun asi, la referencia operativa es la siguiente:

- acuse de recibo en un plazo objetivo de 5 dias habiles
- primera valoracion de severidad y alcance en un plazo objetivo de 10 dias habiles
- coordinacion de mitigacion o correccion cuando el hallazgo sea reproducible

Estos plazos son objetivos razonables, no una garantia contractual. Si la incidencia depende de terceros, infraestructura externa o credenciales no reproducibles, la resolucion puede requerir mas tiempo.

## Divulgacion responsable

- Evita la divulgacion publica completa mientras no exista una mitigacion razonable o una correccion desplegable.
- Comparte solo la informacion necesaria para reproducir y validar el problema.
- Si el fallo afecta a integraciones externas, coordina el reporte con el proveedor correspondiente cuando sea necesario.
- Cuando una correccion llegue a una rama publica, el detalle tecnico debe publicarse con el nivel justo para aprendizaje y auditoria, no para facilitar abuso inmediato.

## Practicas de seguridad presentes en el proyecto

Las siguientes medidas estan respaldadas por la implementacion actual del repositorio:

- autenticacion del panel mediante JWT firmado y validado en backend
- proteccion CSRF stateless con patron double-submit cookie en endpoints de escritura
- limitacion de peticiones con Flask-Limiter, con limites generales y limites especificos en rutas sensibles
- CORS restringido a origenes permitidos configurados mediante `ALLOWED_ORIGINS`
- proteccion del formulario publico con Turnstile, honeypot y sanitizacion de entrada
- cifrado Fernet para claves externas almacenadas en base de datos
- limite maximo de subida configurable en backend para rechazar cargas excesivas
- cabeceras de seguridad en nginx, incluyendo CSP, `X-Frame-Options`, `X-Content-Type-Options` y `Referrer-Policy`
- despliegue publico previsto tras nginx en Railway, con acceso por HTTPS en produccion

## Lo que no debe asumirse

- Este documento no promete monitorizacion 24x7 ni soporte permanente.
- No se debe asumir que un hallazgo tendra parche inmediato si requiere rediseño funcional o depende de terceros.
- No se debe reutilizar en otros entornos la configuracion o credenciales de desarrollo documentadas para uso local.

## Buenas practicas al reportar

- Redacta el impacto en terminos de negocio y de datos afectados.
- Indica si el problema exige autenticacion o si afecta al formulario publico.
- Si adjuntas pruebas, elimina credenciales reales y datos personales.
- Si el problema depende de configuracion local, especifica variables, version de navegador o ruta exacta.

Gracias por ayudar a mantener el proyecto utilizable y seguro sin exponer de forma innecesaria a usuarios, mantenedores o terceros.