from django.contrib.auth import aauthenticate
from django.http.request import HttpRequest
from strawberry.extensions import SchemaExtension
from strawberry.utils.await_maybe import AwaitableOrValue

from .settings import firebase_auth_settings


class FirebaseAuthStrawberryExtension(SchemaExtension):
    """Authenticate Firebase user and inject request.user into GraphQL context."""

    async def on_operation(self) -> AwaitableOrValue[None]:
        request: HttpRequest = self.execution_context.context.request
        token = self._get_token(request)

        if not token:
            return

        user = await self._authenticate_request(request, token)

        if user is not None:
            # Keep both attributes for async Django request handling.
            request._acached_user = user  # pylint: disable=protected-access
            request.user = user

    async def _authenticate_request(self, request: HttpRequest, token: str):
        # Normalize header to pure JWT so backend verification works.
        original_header = request.META.get(firebase_auth_settings.AUTH_HEADER_NAME, "")
        request.META[firebase_auth_settings.AUTH_HEADER_NAME] = token
        try:
            return await aauthenticate(request)
        finally:
            request.META[firebase_auth_settings.AUTH_HEADER_NAME] = original_header

    def _get_token(self, request: HttpRequest) -> str | None:
        auth_data = request.META.get(firebase_auth_settings.AUTH_HEADER_NAME, "").split()

        if len(auth_data) == 1 and auth_data[0]:
            return auth_data[0]

        if len(auth_data) == 2 and auth_data[0].lower() == "bearer":
            return auth_data[1]

        return None
