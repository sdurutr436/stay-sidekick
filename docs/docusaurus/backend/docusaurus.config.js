// @ts-check
// =============================================================================
// DOCUSAURUS — Sitio de documentación de "backend/" (Flask + Python 3.12)
// Publicado en GitHub Pages bajo /stay-sidekick/backend/
//
// La API auto-generada con pydoc-markdown se vuelca en docs/api/ como Markdown
// por el script "prebuild", y Docusaurus la sirve sin más config.
// =============================================================================

const { themes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Stay Sidekick — API Flask',
  tagline: 'Documentación de la API REST en Python 3.12 (Flask + SQLAlchemy + JWT)',
  favicon: 'img/favicon.ico',

  url: 'https://sdurutr436.github.io',
  baseUrl: '/stay-sidekick/backend/',

  organizationName: 'sdurutr436',
  projectName: 'stay-sidekick',
  trailingSlash: true,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

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
            'https://github.com/sdurutr436/stay-sidekick/edit/main/docs/docusaurus/backend/',
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
      navbar: {
        title: 'Stay Sidekick · backend',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'backendSidebar',
            position: 'left',
            label: 'Documentación',
          },
          {
            href: 'https://github.com/sdurutr436/stay-sidekick/tree/main/backend',
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
        additionalLanguages: ['python', 'bash', 'json', 'sql'],
      },
    }),
};

module.exports = config;
