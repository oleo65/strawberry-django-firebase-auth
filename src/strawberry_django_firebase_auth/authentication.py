import logging
from typing import Any

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from firebase_admin import auth

from strawberry_django_firebase_auth.apps import firebase_app

from .settings import firebase_auth_settings

User = get_user_model()


class FirebaseAuthentication:

    def _get_auth_token(self, request) -> dict[str, Any] | None:
        encoded_token = request.META.get(
            firebase_auth_settings.AUTH_HEADER_NAME)
        decoded_token = None

        try:
            decoded_token = auth.verify_id_token(encoded_token, firebase_app)
        except ValueError:
            pass
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError,
                auth.RevokedIdTokenError) as err:
            logging.error(err.default_message)
        except auth.CertificateFetchError as err:
            logging.exception(err)
        return decoded_token

    async def _get_user_from_firebase_user(self, firebase_user: dict[str,
                                                                     Any]):
        firebase_uid = firebase_user.get('uid')
        user = None

        try:
            if firebase_auth_settings.PROFILE_MODEL:
                expression = f"{firebase_auth_settings.PROFILE_MODEL}__{firebase_auth_settings.FIREBASE_UID_PROPERTY}"
            else:
                expression = firebase_auth_settings.FIREBASE_UID_PROPERTY

            user = await User.objects.aget(**{expression: firebase_uid})
        except User.DoesNotExist:
            user = await self._register_unregistered_user(firebase_user)
        return user

    async def _register_unregistered_user(self, firebase_user: dict[str, Any]):
        user = None

        user = await self._match_user_by_email(firebase_user)

        if user is None:
            user = await User.objects.acreate_user(
                username=firebase_user['uid'],
                email=firebase_user['email'],
            )

            user = await self._set_firebase_uid(user, firebase_user)

        return user

    async def _match_user_by_email(self, firebase_user):
        user = None

        try:
            user = await User.objects.aget(email=firebase_user['email'])

            user = await self._set_firebase_uid(user, firebase_user)
        except User.DoesNotExist:
            pass

        return user

    async def _set_firebase_uid(self, user, firebase_user):
        if firebase_auth_settings.PROFILE_MODEL:
            profile = await sync_to_async(getattr)(user, firebase_auth_settings.PROFILE_MODEL)
            setattr(profile, firebase_auth_settings.FIREBASE_UID_PROPERTY,
                    firebase_user['uid'])
            await profile.asave()
        else:
            user.firebase_uid = firebase_user['uid']
            await user.asave()

        return user

    def authenticate(self, request):
        raise NotImplementedError(
            "Synchronous API is not available for auth anymore. Use async API instead."
        )

    async def aauthenticate(self, request):
        user = None
        firebase_user = self._get_auth_token(request)

        if firebase_user:
            user = await self._get_user_from_firebase_user(firebase_user)
        return user

    def get_user(self, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            user = None
        return user
