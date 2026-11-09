from django.conf import settings
from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from wissenswiki.config import registry


@register()
def check_configuration(app_configs=None, **kwargs):
    errors = []
    if "wissenswiki_core" not in settings.INSTALLED_APPS:
        errors.append(Error("'wissenswiki_core' fehlt in INSTALLED_APPS; dort liegen CSS und JS.",
                            id="wissenswiki.E002"))
    try:
        registry()
    except ImproperlyConfigured as exc:
        errors.append(Error(str(exc), id="wissenswiki.E001"))
    return errors
