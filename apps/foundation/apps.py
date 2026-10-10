from django.apps import AppConfig


class FoundationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.foundation'
    verbose_name = 'Fundação (Fase 0)'

    def ready(self):
        # Register signals (auto-create UserProfile, etc.)
        from . import signals  # noqa: F401
