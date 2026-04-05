// =============================================================================
// DATA: CONFIG
// Variables de entorno expuestas a todas las plantillas Nunjucks como
// {{ config.* }}
//
// Carga .env desde web/ (local dev). En Docker el ARG TURNSTILE_SITE_KEY
// se inyecta como ENV antes de npm run build, por lo que process.env ya
// tiene el valor sin necesidad de leer el archivo.
// =============================================================================

require('dotenv').config();

module.exports = {
  turnstileSiteKey: process.env.TURNSTILE_SITE_KEY || '',
};
