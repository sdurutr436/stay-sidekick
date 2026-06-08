// =============================================================================
// SITE DATA — disponible en todas las plantillas como {{ site.* }}
//
// 11ty carga automáticamente cualquier .js bajo web/src/_data/ y expone su
// export por defecto bajo el nombre del archivo. Cualquier cambio aquí
// se refleja en TODAS las páginas en el siguiente build.
//
// Mantener esta estructura sincronizada con:
//   - frontend/src/app/components/organisms/footer/footer.html
//     (el organismo Angular consume las mismas claves vía constantes)
//   - schema.org JSON-LD del <head> en _includes/layouts/base.njk
// =============================================================================

/**
 * @typedef {Object} FooterLink
 * @property {string} text  Etiqueta visible del enlace.
 * @property {string} href  Ruta interna absoluta (`/legal/cookies/`) o URL externa completa.
 *
 * @typedef {Object} FooterGroup
 * @property {string}        label  Cabecera del grupo en la columna del footer.
 * @property {FooterLink[]}  links  Enlaces que cuelgan del grupo. Orden = orden visual.
 *
 * @typedef {Object} SocialLink
 * @property {string} label  Texto accesible para `aria-label` (lectores de pantalla).
 * @property {string} href   URL absoluta del perfil social (HTTPS). `target="_blank" + rel="noopener noreferrer"` al renderizar.
 * @property {string} text   Texto visible del enlace en el footer.
 *
 * @typedef {Object} SiteData
 * @property {string}         name            Marca; se usa como `<title>` por defecto y suffix del resto de páginas.
 * @property {string}         description     Tagline / meta description global por defecto.
 * @property {number}         year            Año actual; útil para copyrights o composiciones de meta.
 * @property {string}         url             Origen público canónico (sin barra final). Se concatena con `page.url` para `canonical` y OG.
 * @property {string}         appUrl          Path bajo el que nginx sirve la SPA Angular (`/menu` en este stack).
 * @property {string}         brandLogo       Logo principal corporativo (light) referenciado desde meta tags.
 * @property {string}         socialImage     OG / Twitter card por defecto (1024×576 light-mode). Pueden sobreescribirla las páginas vía frontmatter `socialImage`.
 * @property {string}         socialImageAlt  Texto alternativo del OG image (sobrescribible por `socialImageAlt` en frontmatter).
 * @property {FooterGroup[]}  footerNav       Columnas centrales del footer; itera el partial `partials/footer.njk`.
 * @property {SocialLink[]}   social          Última columna del footer (perfiles externos). Se abre en nueva pestaña.
 */

/** @type {SiteData} */
module.exports = {
  name: "Stay Sidekick",
  description: "Plataforma web para gestionar solicitudes de estancia y operaciones de alojamiento.",
  year: new Date().getFullYear(),
  // URL pública actual del servicio nginx en Railway
  url: "https://stay-sidekick.up.railway.app",
  // URL pública de la SPA Angular detrás de nginx
  appUrl: "/menu",
  brandLogo: "/assets/img/header/stay-sidekick-512x256-light-mode.png",
  socialImage: "/assets/img/header/stay-sidekick-1024x576-light-mode.png",
  socialImageAlt: "Identidad visual de Stay Sidekick en modo claro",

  footerNav: [
    {
      label: "Producto",
      links: [
        { text: "Funcionalidades", href: "/producto/funcionalidades/" },
        { text: "Precios", href: "/precios/" },
      ],
    },
    {
      label: "Legal",
      links: [
        { text: "Política de privacidad", href: "/legal/privacidad/" },
        { text: "Términos de uso", href: "/legal/terminos/" },
        { text: "Política de cookies", href: "/legal/cookies/" },
      ],
    },
    {
      label: "Empresa",
      links: [
        { text: "Sobre nosotros", href: "/empresa/sobre-nosotros/" },
        { text: "Contacto", href: "/empresa/contacto/" },
      ],
    },
  ],

  social: [
    {
      label: "Perfil de GitHub de Sergio Durán Utrera",
      href: "https://github.com/sdurutr436",
      text: "GitHub",
    },
    {
      label: "Perfil de LinkedIn de Sergio Durán Utrera",
      href: "https://www.linkedin.com/in/sergio-dur%C3%A1n-utrera/",
      text: "LinkedIn",
    },
  ],
};
