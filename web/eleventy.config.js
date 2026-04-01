// =============================================================================
// ELEVENTY CONFIGURATION
// Sitio estático — Stay Sidekick
// Motor de plantillas: Nunjucks
// SCSS compilado externamente desde ../frontend/src/styles/ (ver package.json)
// =============================================================================

module.exports = function (eleventyConfig) {
  // ---------------------------------------------------------------------------
  // Passthrough copy — archivos que se copian tal cual al output
  // ---------------------------------------------------------------------------
  eleventyConfig.addPassthroughCopy("src/assets/images");
  eleventyConfig.addPassthroughCopy("src/assets/fonts");
  // Nota: el CSS se compila directamente a _site/ por el proceso sass externo.
  // No se registra como passthrough para evitar conflictos.

  // ---------------------------------------------------------------------------
  // Watch targets adicionales
  // 11ty reconstruye cuando cambian los estilos compartidos con Angular
  // ---------------------------------------------------------------------------
  eleventyConfig.addWatchTarget("../frontend/src/styles/");

  // ---------------------------------------------------------------------------
  // Shortcodes globales
  // ---------------------------------------------------------------------------
  eleventyConfig.addShortcode("year", () => String(new Date().getFullYear()));

  // ---------------------------------------------------------------------------
  // Retorno de configuración
  // ---------------------------------------------------------------------------
  return {
    templateFormats: ["njk", "html", "md"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_includes/layouts",
      data: "_data",
    },
  };
};
