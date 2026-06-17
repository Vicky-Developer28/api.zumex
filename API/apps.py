from django.apps import AppConfig
from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "API"

    def ready(self):
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            username = getattr(settings, "SUPER_USER", None)
            email = getattr(settings, "SUPER_USER_EMAIL", None)
            password = getattr(settings, "SUPER_USER_PWD", None)

            if not all([username, email, password]):
                return

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )

        except Exception:
            pass
