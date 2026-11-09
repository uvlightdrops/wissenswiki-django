---
project: wissenswiki-django
scope: Überblick, Einbindung und Tests der Wiki-App
created: null
updated: "2026-11-09 11"
update_reason: Kern und Oberfläche nach wissenswiki-core ausgelagert
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

```python
INSTALLED_APPS += ["wissenswiki_core", "wissenswiki"]   # Core liefert CSS/JS
WISSENSWIKI = {
    "WORKSPACE": "~/dev_wiki",                      # optional; Editor
    "DOMAINS": [{"name": "Dokumentation", "source": "/repo/doc",
                 "relations": "~/dev_wiki_rel"}],   # optional; nur lesend
    "MARKDOWN_DATA": {"root": "~/dev_data/ki-knowledge",
                      "relations": "~/dev_wiki_rel_ki", "prefix": "ki:"},  # optional
}
# urls.py
path("wiki/", include("wissenswiki.urls"))
```

Seiten: `wiki/` (Arbeitsraum), `wiki/graph/`, `wiki/graph-header/`, `wiki/settings/`.

## Tests [tests]

```bash
pip install -e ../wissenswiki-core -e '.[test]'
python -m pytest -q
```

Beispiel-Host: `../ki-knowledge-next`.
