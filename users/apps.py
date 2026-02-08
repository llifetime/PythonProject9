from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        # Убираем импорт сигналов, если их нет
        try:
            import users.signals  # Если будут сигналы
        except ImportError:
            pass
