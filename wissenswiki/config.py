"""Registry from ``settings.WISSENSWIKI``; schema see ``wissenswiki_core.registry``."""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver

from wissenswiki_core.registry import ConfigError, Registry, build_registry


@lru_cache(maxsize=1)
def registry() -> Registry:
    """Configured workspace and domains; cached until the setting changes."""
    config = getattr(settings, "WISSENSWIKI", None)
    if config is None:
        raise ImproperlyConfigured("WISSENSWIKI fehlt in den Django-Settings.")
    try:
        return build_registry(config)
    except ConfigError as exc:
        raise ImproperlyConfigured(f"WISSENSWIKI: {exc}") from exc


@receiver(setting_changed)
def _reset(setting: str, **kwargs) -> None:
    if setting == "WISSENSWIKI":
        registry.cache_clear()
