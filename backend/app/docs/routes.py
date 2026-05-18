"""Blueprint de documentación: Swagger UI + spec OpenAPI.

Rutas públicas:
- GET /api/docs              → Swagger UI
- GET /api/docs/openapi.yaml → Spec OpenAPI 3.0 en YAML
"""

import os

from flask import Blueprint, Response, render_template_string, send_file, url_for

docs_bp = Blueprint("docs", __name__, static_folder="static", static_url_path="/api/docs/static")

_SPEC_PATH = os.path.join(os.path.dirname(__file__), "openapi.yaml")


@docs_bp.route("/api/docs")
def swagger_ui():
    init_script_url = url_for("docs.static", filename="swagger-init.js")
    return Response(
        render_template_string(
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
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
<script src="{{ init_script_url }}"></script>
</body>
</html>""",
            init_script_url=init_script_url,
        ),
        mimetype="text/html",
    )


@docs_bp.route("/api/docs/openapi.yaml")
def openapi_spec():
    return send_file(_SPEC_PATH, mimetype="application/yaml")
