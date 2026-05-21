// =============================================================================
// SITE DATA — disponible en todas las plantillas como {{ site.* }}
// =============================================================================

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
