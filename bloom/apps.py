from django.apps import AppConfig


class BloomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bloom"

    def ready(self):
        import bloom.signals  # Import signals to register them
