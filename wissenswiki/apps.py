from django.apps import AppConfig


class WissenswikiConfig(AppConfig):
    name = "wissenswiki"
    verbose_name = "Wissenswiki"

    def ready(self) -> None:
        from wissenswiki import checks, config  # noqa: F401  (registers check and signal)
