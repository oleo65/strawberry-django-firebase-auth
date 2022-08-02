from django.contrib.auth import authenticate
from .settings import firebase_auth_settings
from strawberry.utils.await_maybe import AwaitableOrValue
from strawberry.extensions import Extension
from django.http.request import HttpRequest


class FirebaseAuthStrawberryExtension(Extension):
    """Extension to be used with strawberry to authenticate the firebase user via token."""

    def on_request_start(self) -> AwaitableOrValue[None]:
        request: HttpRequest = self.execution_context.context.request
        token = self._get_token(request)

        if token is not None:
            user = authenticate(request=request)

            if user is not None:
                request.user = user

    def _get_token(self, request: HttpRequest):
        auth_data = request.META.get(firebase_auth_settings.AUTH_HEADER_NAME, '').split()

        if len(auth_data) == 1 and auth_data[0] != '':
            return auth_data[0]
        elif len(auth_data) == 2:
            return auth_data[1]

        return None
