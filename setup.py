import os
from setuptools import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='strawberry_django_firebase_auth',
    version='0.9.0',
    author='Ole Odendahl',
    author_email='oleodendahl@gmail.com',
    description=(
        "Authentication provider for strawberry-django and Google Firebase's "
        "Authentication service."
    ),
    license='MIT',
    keywords='strawberry django firebase auth',
    url='https://github.com/oleo65/strawberry-django-firebase-auth',
    packages=['strawberry_django_firebase_auth'],
    install_requires=['django', 'firebase-admin', 'strawberry-graphql'],
    long_description=README,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
