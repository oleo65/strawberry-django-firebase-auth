from django.apps import AppConfig
from django.conf import settings
import firebase_admin
from .settings import firebase_auth_settings


firebase_app = None


class FirebaseAuthConfig(AppConfig):
    name = 'strawberry_django_firebase_auth'

    def ready(self):
        if firebase_auth_settings.AUTO_CREATE_FIREBASE_APP:
            credentials = firebase_admin.credentials.Certificate(
                settings.GOOGLE_APPLICATION_CREDENTIALS,
            )
            global firebase_app
            firebase_app = firebase_admin.initialize_app(credentials)
