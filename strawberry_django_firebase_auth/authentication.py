import logging

from django.contrib.auth import get_user_model
from firebase_admin import auth

from strawberry_django_firebase_auth.apps import firebase_app

from .settings import firebase_auth_settings

User = get_user_model()


class FirebaseAuthentication:

    def _get_auth_token(self, request):
        encoded_token = request.META.get(firebase_auth_settings.AUTH_HEADER_NAME)
        decoded_token = None

        try:
            decoded_token = auth.verify_id_token(encoded_token, firebase_app)
        except ValueError:
            pass
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError) as err:
            logging.error(err.default_message)
        except auth.CertificateFetchError as err:
            logging.exception(err)
        return decoded_token

    def _get_user_from_firebase_user(self, firebase_user):
        firebase_uid = firebase_user.get('uid')
        user = None

        try:
            if firebase_auth_settings.PROFILE_MODEL:
                expression = f"{firebase_auth_settings.PROFILE_MODEL}__{firebase_auth_settings.FIREBASE_UID_PROPERTY}"
            else:
                expression = firebase_auth_settings.FIREBASE_UID_PROPERTY

            user = User.objects.get(**{expression: firebase_uid})
        except User.DoesNotExist:
            user = self._register_unregistered_user(firebase_user)
        return user

    def _register_unregistered_user(self, firebase_user):
        user = None

        user = self._match_user_by_email(firebase_user)

        if user is None:
            user = User.objects.create_user(
                username=firebase_user['uid'],
                email=firebase_user['email'],
            )

            user = self._set_firebase_uid(user, firebase_user)

        return user

    def _match_user_by_email(self, firebase_user):
        user = None

        try:
            user = User.objects.get(email=firebase_user['email'])

            user = self._set_firebase_uid(user, firebase_user)
        except User.DoesNotExist:
            pass

        return user

    def _set_firebase_uid(self, user, firebase_user):
        if firebase_auth_settings.PROFILE_MODEL:
            profile = getattr(user, firebase_auth_settings.PROFILE_MODEL)
            setattr(profile, firebase_auth_settings.FIREBASE_UID_PROPERTY, firebase_user['uid'])
            profile.save()
        else:
            user.firebase_uid = firebase_user['uid']
            user.save()

        return user

    def authenticate(self, request):
        user = None
        firebase_user = self._get_auth_token(request)

        if firebase_user:
            user = self._get_user_from_firebase_user(firebase_user)
        return user

    def get_user(self, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            user = None
        return user
