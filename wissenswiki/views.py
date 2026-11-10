"""Thin Django layer: login, CSRF and URLs around ``wissenswiki_core``."""

from __future__ import annotations

from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from wissenswiki.config import registry
from wissenswiki_core.pages import PageUrls, render_page
from wissenswiki_core.service import ApiError, api_get, api_post


def _urls() -> PageUrls:
    return PageUrls(api=reverse("wissenswiki:api"), static=static(""),
                    workspace=reverse("wissenswiki:workspace"), graph=reverse("wissenswiki:graph"),
                    graph_header=reverse("wissenswiki:graph-header"), settings=reverse("wissenswiki:settings"))


@login_required
def page(request: HttpRequest, page: str) -> HttpResponse:
    current = registry()
    if current.workspace is None:
        if page == "workspace":
            return redirect("wissenswiki:graph")
        if not request.GET.get("domain"):
            return redirect(request.path + "?domain=" + quote(next(iter(current.domains)), safe=""))
    template = getattr(settings, "WISSENSWIKI_NAVIGATION_TEMPLATE", "")
    navigation = render_to_string(template, request=request) if template else ""
    html = render_page(page, urls=_urls(), token=get_token(request), path=request.path,
                       workspace_enabled=current.workspace is not None, domains=current.domains,
                       app_navigation=navigation)
    return HttpResponse(html)


@login_required
@require_http_methods(["GET", "POST"])
def api(request: HttpRequest) -> JsonResponse:
    try:
        if request.method == "GET":
            data = api_get(registry(), request.GET.get("domain", ""))
        else:
            data = api_post(registry(), request.body, request.content_type)
    except ApiError as exc:
        return JsonResponse({"error": str(exc)}, status=exc.status, json_dumps_params={"ensure_ascii": False})
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
