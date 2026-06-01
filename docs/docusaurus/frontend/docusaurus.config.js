// @ts-check
// =============================================================================
// DOCUSAURUS — Sitio de documentación de "frontend/" (Angular 21 + TypeScript)
// Publicado en GitHub Pages bajo /stay-sidekick/frontend/
//
// La API auto-generada con TypeDoc se vuelca en docs/api/ como Markdown
// por el script "prebuild" (typedoc), y Docusaurus la sirve sin más config.
// =============================================================================

const { themes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Stay Sidekick — SPA Angular',
  tagline: 'Documentación del panel privado (Angular 21 + TypeScript)',
  favicon: 'img/favicon.ico',

  url: 'https://sdurutr436.github.io',
  baseUrl: '/stay-sidekick/frontend/',

  organizationName: 'sdurutr436',
  projectName: 'stay-sidekick',
  trailingSlash: true,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Diagramas Mermaid en bloques ```mermaid (necesita @docusaurus/theme-mermaid)
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/sdurutr436/stay-sidekick/edit/main/docs/docusaurus/frontend/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // OG / Twitter card al compartir cualquier URL del sitio
      image: 'img/og-image.png',
      navbar: {
        title: 'Stay Sidekick · frontend',
        logo: {
          alt: 'Stay Sidekick',
          src: 'img/logo.png',
          srcDark: 'img/logo-dark.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'frontendSidebar',
            position: 'left',
            label: 'Documentación',
          },
          {
            href: 'https://github.com/sdurutr436/stay-sidekick/tree/main/frontend',
            label: 'Código en GitHub',
            position: 'right',
          },
          {
            href: 'https://sdurutr436.github.io/stay-sidekick/',
            label: '← Índice de docs',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `© ${new Date().getFullYear()} Sergio Durán · Licencia MIT`,
      },
      prism: {
        theme: themes.github,
        darkTheme: themes.dracula,
        additionalLanguages: ['typescript', 'scss', 'bash', 'json'],
      },
    }),
};

module.exports = config;
