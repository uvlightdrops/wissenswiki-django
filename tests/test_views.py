import json

import pytest
from django.contrib.auth.models import User
from django.core.checks import run_checks
from django.test import Client

pytestmark = pytest.mark.django_db


@pytest.fixture
def wiki(tmp_path, settings):
    workspace = tmp_path / "workspace"
    source, relations = tmp_path / "docs", tmp_path / "rel"
    for path in (workspace, source, relations):
        path.mkdir()
    (source / "a.md").write_text("---\n{}\n---\n# A\n## Eins [eins]\nText\n## Zwei [zwei]\nMehr\n")
    settings.WISSENSWIKI = {"WORKSPACE": str(workspace),
                            "DOMAINS": [{"name": "Doku", "source": str(source), "relations": str(relations)}]}
    return tmp_path


def _client(**kwargs) -> Client:
    client = Client(**kwargs)
    client.force_login(User.objects.create_user("anna"))
    return client


def _token(client: Client, url: str = "/wiki/") -> str:
    page = client.get(url).content.decode()
    return page.split('name="workspace-token" content="', 1)[1].split('"', 1)[0]


def test_pages_require_login(wiki):
    for url in ("/wiki/", "/wiki/api", "/wiki/graph/", "/wiki/graph-header/", "/wiki/settings/"):
        response = Client().get(url)
        assert response.status_code == 302 and response["Location"].startswith("/login/")


def test_pages_render_django_urls_and_relation_types(wiki):
    client = _client()
    page = client.get("/wiki/graph-header/").content.decode()
    assert 'content="/wiki/api"' in page
    assert '/static/wissenswiki/graph.js' in page
    assert 'href="/wiki/settings/"' in page
    assert 'href="/wiki/graph-header/?domain=Doku"' in page
    assert 'value="depends-on" checked' in page
    for url in ("/wiki/", "/wiki/graph/", "/wiki/settings/"):
        assert client.get(url).status_code == 200


def test_workspace_api_creates_and_relates_blocks_with_csrf(wiki):
    client = _client(enforce_csrf_checks=True)
    token = _token(client)
    post = lambda data, **headers: client.post("/wiki/api", json.dumps(data), content_type="application/json",
                                                **headers)

    assert post({"action": "create", "title": "X", "text": ""}).status_code == 403
    first = post({"action": "create", "title": "Eins", "text": "A"}, HTTP_X_CSRFTOKEN=token).json()
    second = post({"action": "create", "title": "Zwei", "text": "B"}, HTTP_X_CSRFTOKEN=token).json()
    related = post({"action": "graph-relate", "id": first["id"], "revision": first["revision"],
                    "target": second["id"], "type": "extends"}, HTTP_X_CSRFTOKEN=token)
    assert related.json()["relations"] == [{"target": second["id"], "type": "extends"}]
    stale = post({"action": "save", "id": first["id"], "revision": first["revision"],
                  "title": "Neu", "text": ""}, HTTP_X_CSRFTOKEN=token)
    assert stale.status_code == 409
    assert len(client.get("/wiki/api").json()["blocks"]) == 2
    assert client.post("/wiki/api", "x", content_type="text/plain", HTTP_X_CSRFTOKEN=token).status_code == 415


def test_domain_api_saves_relation_beside_sources(wiki):
    client = _client(enforce_csrf_checks=True)
    token = _token(client)
    snapshot = client.get("/wiki/api", {"domain": "Doku"}).json()
    response = client.post("/wiki/api", json.dumps({
        "action": "graph-relate", "domain": "Doku", "id": "doc:a.md#eins", "target": "doc:a.md#zwei",
        "type": "references", "revision": snapshot["revision"]}), content_type="application/json",
        HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200
    assert json.loads((wiki / "rel" / "dokument-beziehungen.json").read_text())[0]["type"] == "references"
    assert client.get("/wiki/api", {"domain": "Fehlt"}).status_code == 400


def test_without_workspace_pages_redirect_to_first_domain(wiki, settings):
    settings.WISSENSWIKI = {"DOMAINS": settings.WISSENSWIKI["DOMAINS"]}
    client = _client()
    assert client.get("/wiki/").url == "/wiki/graph/"
    assert client.get("/wiki/graph/").url == "/wiki/graph/?domain=Doku"


def test_system_check_reports_configuration_errors(wiki, settings):
    assert not [m for m in run_checks() if m.id == "wissenswiki.E001"]
    settings.WISSENSWIKI = {"WORKSPACE": str(wiki / "fehlt")}
    errors = [m for m in run_checks() if m.id == "wissenswiki.E001"]
    assert errors and "existiert nicht" in errors[0].msg
    settings.WISSENSWIKI = {"WORKSPAC": "x"}
    assert "unbekannte" in [m for m in run_checks() if m.id == "wissenswiki.E001"][0].msg


def test_static_assets_come_from_core_app(settings):
    from django.contrib.staticfiles import finders

    assert finders.find("wissenswiki/graph.js")
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != "wissenswiki_core"]
    assert [m for m in run_checks() if m.id == "wissenswiki.E002"]
