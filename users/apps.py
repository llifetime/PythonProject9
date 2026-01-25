from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Users'

    def ready(self):
        """Импорт сигналов при загрузке приложения"""
        try:
            import users.signals  # noqa: F401
        except ImportError:
            pass