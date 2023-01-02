from django.apps import AppConfig
from .models import Database


class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_app'

    def ready(self):
        Database.init_models()
