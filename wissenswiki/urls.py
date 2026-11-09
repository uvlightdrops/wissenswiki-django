from django.urls import path

from wissenswiki import views

app_name = "wissenswiki"

urlpatterns = [
    path("", views.page, {"page": "workspace"}, name="workspace"),
    path("api", views.api, name="api"),
    path("graph/", views.page, {"page": "graph"}, name="graph"),
    path("graph-header/", views.page, {"page": "graph-header"}, name="graph-header"),
    path("settings/", views.page, {"page": "settings"}, name="settings"),
]
