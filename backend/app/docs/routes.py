"""Blueprint de documentación: Swagger UI + spec OpenAPI.

Rutas (públicas):
- GET /api/docs            → Swagger UI (sin autenticación, solo en DEBUG)
- GET /api/docs/openapi.yaml → Spec OpenAPI 3.0 en YAML
"""

import os

from flask import Blueprint, Response, current_app, send_file

docs_bp = Blueprint("docs", __name__)

_SPEC_PATH = os.path.join(os.path.dirname(__file__), "openapi.yaml")


@docs_bp.route("/api/docs")
def swagger_ui():
    return Response(
        """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Stay Sidekick — API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>body{margin:0}.swagger-ui .topbar{background:#1a1a2e}</style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
  window.onload = () => SwaggerUIBundle({
    url: "/api/docs/openapi.yaml",
    dom_id: "#swagger-ui",
    deepLinking: true,
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
    layout: "BaseLayout",
    persistAuthorization: true,
  });
</script>
</body>
</html>""",
        mimetype="text/html",
    )


@docs_bp.route("/api/docs/openapi.yaml")
def openapi_spec():
    return send_file(_SPEC_PATH, mimetype="application/yaml")
