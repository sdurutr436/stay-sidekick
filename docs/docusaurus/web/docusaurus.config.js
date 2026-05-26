// @ts-check
// =============================================================================
// DOCUSAURUS — Sitio de documentación de "web/" (11ty + Nunjucks)
// Publicado en GitHub Pages bajo /stay-sidekick/web/
// =============================================================================

const { themes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Stay Sidekick — Sitio estático (11ty)',
  tagline: 'Documentación de la landing pública construida con 11ty + Nunjucks',
  favicon: 'img/favicon.ico',

  // URL pública (raíz del dominio GitHub Pages del usuario)
  url: 'https://sdurutr436.github.io',
  // Cada sitio Docusaurus cuelga de un subpath distinto del proyecto
  baseUrl: '/stay-sidekick/web/',

  // GitHub Pages (deployment via actions/deploy-pages)
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
            'https://github.com/sdurutr436/stay-sidekick/edit/main/docs/docusaurus/web/',
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
        title: 'Stay Sidekick · web',
        logo: {
          alt: 'Stay Sidekick',
          src: 'img/logo.png',
          srcDark: 'img/logo-dark.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'webSidebar',
            position: 'left',
            label: 'Documentación',
          },
          {
            href: 'https://github.com/sdurutr436/stay-sidekick/tree/main/web',
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
        additionalLanguages: ['scss', 'bash', 'json'],
      },
    }),
};

module.exports = config;
