[![Build and Test](https://github.com/oleo65/strawberry-django-firebase-auth/actions/workflows/pythonpackage.yml/badge.svg?branch=master)](https://github.com/oleo65/strawberry-django-firebase-auth/actions/workflows/pythonpackage.yml)
[![Release](https://github.com/oleo65/strawberry-django-firebase-auth/actions/workflows/pythonpackage.yml/badge.svg?branch=master&event=release)](https://github.com/oleo65/strawberry-django-firebase-auth/actions/workflows/pythonpackage.yml)

# Strawberry Django Firebase Auth

Authentication provider for strawberry-django and Firebase's Authentication service.

It is still somewhat work in progress and contributions are welcome.

Partially inspired by
[graphene-django-firebase-auth](https://github.com/dspacejs/graphene-django-firebase-auth)

This app is used with [Firebase Authentication](https://firebase.google.com/docs/auth/) on a client.

## Compatibility

This code has only been tested with Python `3.10` and Django `4.0.6`.

## Installing

1. Install the app:

```sh
pipenv install strawberry-django-firebase-auth
```

2. Download the JSON file from your [Firebase console](https://console.firebase.google.com/) with your account's credentials.

3. Set `GOOGLE_APPLICATION_CREDENTIALS` in your project's settings to the path of the credentials file:

```python
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'path/to/google-service-account.json')
```

4. Add the authentication backend to `AUTHENTICATION_BACKENDS`:

```python
AUTHENTICATION_BACKENDS = ['strawberry_django_firebase_auth.authentication.FirebaseAuthentication']
```

<!-- 5. Add authentication middleware to `GRAPHENE`

```python
GRAPHENE = {
    'MIDDLEWARE': ['strawberry_django_firebase_auth.middleware.FirebaseAuthStrawberryMiddleware',],
}
``` -->

6. Add `strawberry_django_firebase_auth` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
  '...',
  'strawberry_django_firebase_auth',
]
```

7. Add `FirebaseAuthMixin` to your `AUTH_USER_MODEL`. You need to have a custom user model to make this work.:

```python
from django.contrib.auth.models import AbstractUser
from strawberry_django_firebase_auth.models import FirebaseAuthMixin

class User(AbstractUser, FirebaseAuthMixin):
    pass
```

8. Build and run your DB migrations to add the changes:

```sh
./manage.py makemigrations
./manage.py migrate
```

9. Add the Strawberry Schema extension

```python
from strawberry_django_firebase_auth.extension import FirebaseAuthStrawberryExtension

schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=[FirebaseAuthStrawberryExtension])
```

## Additional configuration

All settings will be bundled in the `STRAWBERRY_FIREBASE_AUTH` dictionary.

```python
STRAWBERRY_FIREBASE_AUTH = {
    'PROFILE_MODEL': 'profile',
    'AUTO_CREATE_FIREBASE_APP': True,
}
```

`AUTO_CREATE_FIREBASE_APP`: (Default: `True`) If you have more than one firebase product in your django app, you might want to control the init workflow centrally in your `settings.py` file. Setting this flag to false will not implicitly initialize the firebase app within this library but assume an already initialized app.

## Using the package

Once installed, authentication will be managed using this package.

The `Firebase JWT Token` is extracted from the header and evaluated by the middleware. It is then send to the authorization backend(s) for validation and django user matching. If successful the `context.user` will be properly populated with the matched user and will be available for further processing.

### How does it work on the backend?

1. The client provides the firebase jwt token via HTTP headers to the django backend via graphql request.
1. The middleware extracts the token from the request context and delegates authentication to the authentication backend.
1. The authentication backend performs multiple steps to authenticate a user.
  1. Validates the token with `Firebase`.
  1. If valid, tries to retrieve a matching django user from the database via `firebase_uid`
  1. If not found, tries to get an user as fallback via email. If found, adds the `firebase_uid` for future reference. This helps linking already existing accounts.
  1. If failed, creates an django user account with the provided infos from `Firebase`, using `firebase_uid` as username and `email` as email.
  1. Returns the user object and performs the login.

### Using the logged in user

You can access `info.context.user` to add authentication logic, such as
with the following:

```python
def resolve_users(self, info, **kwargs):
    success = False

    if info.context.user.is_authenticated:
        success = True
    return success
```

## Sending tokens from the client

Your client will need to send an additional HTTP header `Authorization: <Firebase Token>` on each request.

How you do this depends on your client and is outside the scope of this documentation.

## Developing

### Setting up your environment

1. Install the dependencies:

```sh
pipenv install --dev
```

2. Download the JSON file from your [Firebase console](https://console.firebase.google.com/) with your account's credentials.

3. Create an `.env` file using `.env.example` as a template. Make sure
to specify the path to the file in the previous step.

4. Enter the virtual environment:

```sh
./manage.py shell
```

### Other commands

```sh
# Run the tests
./manage.py test
```
