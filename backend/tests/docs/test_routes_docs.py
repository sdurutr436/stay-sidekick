"""Tests de integración para el blueprint de documentación."""

import pathlib

import pytest
from flask import Flask
import yaml


@pytest.fixture
def client():
    from app.docs.routes import docs_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(docs_bp)
    return app.test_client()


def test_swagger_ui_devuelve_html_con_assets_correctos(client):
    resp = client.get("/api/docs")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'https://unpkg.com/swagger-ui-dist@5/swagger-ui.css' in html
    assert 'https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js' in html
    assert 'https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js' in html
    assert '/api/docs/static/swagger-init.js' in html


def test_swagger_init_js_se_publica_desde_el_blueprint(client):
    resp = client.get("/api/docs/static/swagger-init.js")

    assert resp.status_code == 200
    script = resp.get_data(as_text=True)
    assert 'SwaggerUIStandalonePreset' in script
    assert 'url: "/api/docs/openapi.yaml"' in script


def test_openapi_yaml_se_sirve_desde_el_backend(client):
    resp = client.get("/api/docs/openapi.yaml")

    assert resp.status_code == 200
    assert resp.get_data(as_text=True).startswith("openapi: 3.0.3")


def test_openapi_yaml_no_tiene_claves_duplicadas():
    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key ({key})",
                    key_node.start_mark,
                )
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    UniqueKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping,
    )

    spec_path = pathlib.Path(__file__).resolve().parents[2] / "app" / "docs" / "openapi.yaml"
    spec = yaml.load(spec_path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)

    assert spec["openapi"] == "3.0.3"
