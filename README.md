---
project: wissenswiki-django
scope: Überblick, Einbindung und Tests der Wiki-App
created: null
updated: "2026-11-11 19"
update_reason: Gemeinsamen Betreiberkatalog für Renderer und API beschrieben
status: active
agent_project: ki-knowledge
---

# wissenswiki-django

Django-App für das Wissenswiki: Mit dem Eintrag in `INSTALLED_APPS` ist es in jeder Django-Site verfügbar.
Kern, Oberfläche und API kommen aus `wissenswiki-core` (`../wissenswiki-core`).
Diese App ergänzt nur Login, CSRF, URL-Routing und die Konfiguration über die Settings.

## Aufbau [package-layout]

| Teil | Zweck |
|------|-------|
| `wissenswiki/config.py` | `settings.WISSENSWIKI` → `wissenswiki_core.registry`; Fehler als `ImproperlyConfigured` |
| `wissenswiki/views.py`, `urls.py` | Seiten und JSON-API über `wissenswiki_core.pages` und `.service` |
| `wissenswiki/checks.py` | Systemprüfungen `wissenswiki.E001` (Konfiguration), `E002` (Core-App fehlt) |

## Einbindung [integration]

```yaml block-meta
updated: "2026-11-11 19"
status: active
relations:
  - target: ../wissenswiki-core/README.md#relation-catalog
    type: depends-on
    reason: Gemeinsames Katalogschema, Definitionen und API-Vertrag des Core
```

```python
INSTALLED_APPS += ["wissenswiki_core", "wissenswiki"]   # Core liefert CSS/JS
WISSENSWIKI = {
    "WORKSPACE": "~/dev_wiki",                      # optional; Editor
    "DOMAINS": [{"name": "Dokumentation", "source": "/repo/doc",
                 "relations": "~/dev_wiki_rel"}],   # optional; nur lesend
    "MARKDOWN_DATA": {"root": "~/dev_data/ki-knowledge",
                      "relations": "~/dev_wiki_rel_ki", "prefix": "ki:"},  # optional
    "RELATION_CATALOG": {"preset": "documentation", "types": []},  # optional
}
# urls.py
path("wiki/", include("wissenswiki.urls"))
```

Seiten: `wiki/` (Arbeitsraum), `wiki/graph/`, `wiki/graph-header/`, `wiki/settings/`.

Der [Beziehungskatalog des Core](../wissenswiki-core/README.md#relation-catalog)
gilt unverändert in Django: `basic`, `documentation` (Standard), `knowledge`
und eigene Typen. Seiten erhalten den aktuellen Katalog; GET `wiki/api`
liefert `relation_types` mit `key`, `label`, `description`, `color`, `enabled`.
Arbeitsraum- und Netz-Schreibaktionen validieren dieselben aktivierten Typen.
Ungültige Konfiguration wird als `ImproperlyConfigured` beziehungsweise
Systemprüfung `wissenswiki.E001` gemeldet; deaktivierte bestehende Kanten bleiben lesbar.

Optional kann der Host `WISSENSWIKI_NAVIGATION_TEMPLATE = "navigation.html"`
setzen. Dieses Django-Template wird mit dem aktuellen Request und den
konfigurierten Context Processors gerendert und am Anfang jeder Wiki-Seite
eingebunden. Es darf vertrauenswürdiges Host-Markup und eigene CSS-/JS-Links
enthalten, aber keine ungeprüften Nutzereingaben. Ohne diese Einstellung
bleibt die Oberfläche unverändert; ein fehlendes Template wird als Fehler
gemeldet.

## Tests [tests]

```bash
pip install -e ../wissenswiki-core -e '.[test]'
python -m pytest -q
```

Beispiel-Host: `../ki-knowledge-next`.
