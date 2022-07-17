from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULTS = {
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "FIREBASE_UID_PROPERTY": "firebase_uid",
    "PROFILE_MODEL": "",
    "AUTO_CREATE_FIREBASE_APP": True,
}

def perform_import(value, setting_name):
    if isinstance(value, str):
        return import_from_string(value, setting_name)
    if isinstance(value, (list, tuple)):
        return [import_from_string(item, setting_name) for item in value]
    return value


def import_from_string(value, setting_name):
    try:
        return import_string(value)
    except ImportError as e:
        msg = (
            f'Could not import `{value}` for setting `{setting_name}`.'
            f'{e.__class__.__name__}: {e}.'
        )
        raise ImportError(msg)


class FirebaseAuthSettings:
    """
    Settings supplied via dictionary named `STRAWBERRY_FIREBASE_AUTH` in Django settings file.
    """

    def __init__(self, defaults):
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f'Invalid setting: `{attr}`')

        value = self.user_settings.get(attr, self.defaults[attr])

        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'STRAWBERRY_FIREBASE_AUTH', {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


def reload_settings(*args, **kwargs):
    setting = kwargs['setting']

    if setting == 'STRAWBERRY_FIREBASE_AUTH':
        firebase_auth_settings.reload()


setting_changed.connect(reload_settings)

firebase_auth_settings = FirebaseAuthSettings(DEFAULTS)
