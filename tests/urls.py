from django.urls import include, path

urlpatterns = [path("wiki/", include("wissenswiki.urls"))]
