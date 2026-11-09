from pathlib import Path

SECRET_KEY = "tests-only"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "wissenswiki_core",
    "wissenswiki",
]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
ROOT_URLCONF = "tests.urls"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STATIC_URL = "/static/"
LOGIN_URL = "/login/"
USE_TZ = True
# Tests that use the API override this with their own temporary folders.
WISSENSWIKI = {"WORKSPACE": str(Path(__file__).parent / "fixtures" / "workspace")}
