"""Adapter catalog integration without database access."""

import json
from types import SimpleNamespace

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory

from wissenswiki.config import registry
from wissenswiki.views import api, page
from wissenswiki_core.relations import DEFAULT_CATALOG


@pytest.fixture
def configured(tmp_path, settings):
    for name in ("workspace", "docs", "relations"):
        (tmp_path / name).mkdir()
    (tmp_path / "docs" / "a.md").write_text("---\n{}\n---\n# A\n## One [one]\n## Two [two]")
    settings.WISSENSWIKI = {
        "WORKSPACE": str(tmp_path / "workspace"),
        "DOMAINS": [{"name": "Docs", "source": str(tmp_path / "docs"), "relations": str(tmp_path / "relations")}],
        "RELATION_CATALOG": {"preset": "basic", "types": [
            {"key": "informs", "label": "Informiert", "description": "Der Ausgang informiert das Ziel.", "color": "#123abc"},
            {**next(item.as_dict() for item in DEFAULT_CATALOG if item.key == "depends-on"), "enabled": False},
        ]},
    }


def request(method, data=None, domain=""):
    factory = RequestFactory()
    result = factory.get("/wiki/api", {"domain": domain}) if method == "GET" else factory.post(
        "/wiki/api", json.dumps(data), content_type="application/json")
    result.user = SimpleNamespace(is_authenticated=True)
    return result


def test_adapter_renders_and_returns_current_catalog_without_database(configured):
    snapshot = json.loads(api(request("GET")).content)
    definitions = snapshot["relation_types"]
    assert definitions == json.loads(api(request("GET", domain="Docs")).content)["relation_types"]
    assert definitions[-1] == {
        "key": "informs", "label": "Informiert", "description": "Der Ausgang informiert das Ziel.",
        "color": "#123abc", "enabled": True}
    for view in ("workspace", "graph", "graph-header"):
        html = page(request("GET"), view).content.decode()
        assert 'value="informs"' in html and 'value="depends-on"' not in html
        assert "Informiert (informs)" in html and "Der Ausgang informiert das Ziel." in html


def test_adapter_validates_workspace_and_document_actions_against_catalog(configured):
    current = registry()
    first, second = current.workspace.create("A", ""), current.workspace.create("B", "")
    for action in ("relate", "graph-relate"):
        response = api(request("POST", {"action": action, "id": first["id"], "revision": first["revision"],
                                       "target": second["id"], "type": "depends-on"}))
        assert response.status_code == 400 and "deaktivierter" in json.loads(response.content)["error"]
    response = api(request("POST", {"action": "relate", "id": first["id"], "revision": first["revision"],
                                   "target": second["id"], "type": "informs"}))
    assert response.status_code == 200
    snapshot = json.loads(api(request("GET", domain="Docs")).content)
    payload = {"action": "graph-relate", "domain": "Docs", "id": "doc:a.md#one",
               "target": "doc:a.md#two", "revision": snapshot["revision"], "type": "depends-on"}
    assert api(request("POST", payload)).status_code == 400
    payload["type"] = "informs"
    assert api(request("POST", payload)).status_code == 200


def test_adapter_reports_invalid_catalog_as_configuration_error(settings):
    settings.WISSENSWIKI = {"RELATION_CATALOG": {"preset": "missing"}}
    with pytest.raises(ImproperlyConfigured, match="Beziehungspreset"):
        registry()
