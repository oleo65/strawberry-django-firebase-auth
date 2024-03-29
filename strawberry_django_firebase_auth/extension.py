from django.contrib.auth import aauthenticate
from django.http.request import HttpRequest
from strawberry.extensions import SchemaExtension
from strawberry.utils.await_maybe import AwaitableOrValue

from .settings import firebase_auth_settings


class FirebaseAuthStrawberryExtension(SchemaExtension):
    """Extension to be used with strawberry to authenticate the firebase user via token."""

    async def on_request_start(self) -> AwaitableOrValue[None]:
        request: HttpRequest = self.execution_context.context.request
        token = self._get_token(request)

        if token is not None:
            user = await self._authenticate_request(request)

            if user is not None:
                # FIXME: Hack for async resolve due to possible Django bug not relaying the get_user to the proper backend.
                request._acached_user = user    # pylint: disable=protected-access
                request.user = user

    async def _authenticate_request(self, request):
        return await aauthenticate(request)
        # return await sync_to_async(authenticate)(request=request)

    def _get_token(self, request: HttpRequest):
        auth_data = request.META.get(firebase_auth_settings.AUTH_HEADER_NAME, '').split()

        if len(auth_data) == 1 and auth_data[0] != '':
            return auth_data[0]
        elif len(auth_data) == 2:
            return auth_data[1]

        return None
