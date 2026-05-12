// =============================================================================
// SITE DATA — disponible en todas las plantillas como {{ site.* }}
// =============================================================================

module.exports = {
  name: "Stay Sidekick",
  description: "La plataforma para gestionar tus solicitudes de estancia.",
  year: new Date().getFullYear(),
  // URL base de producción — ajustar cuando se defina el dominio
  url: "https://stay-sidekick.up.railway.app",
  // URL de la aplicación Angular
  appUrl: "/app",

  footerNav: [
    {
      label: "Producto",
      links: [
        { text: "Funcionalidades", href: "#" },
        { text: "Precios", href: "/precios" },
      ],
    },
    {
      label: "Legal",
      links: [
        { text: "Política de privacidad", href: "/legal/privacidad" },
        { text: "Términos de uso", href: "/legal/terminos" },
        { text: "Política de cookies", href: "/legal/cookies" },
      ],
    },
    {
      label: "Empresa",
      links: [
        { text: "Sobre nosotros", href: "/empresa/sobre-nosotros" },
        { text: "Contacto", href: "/empresa/contacto" },
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
