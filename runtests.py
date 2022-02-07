#!/usr/bin/env python
import django
from django.conf import settings
from django.core.management import call_command

if __name__ == "__main__":
    settings.configure(
        SECRET_KEY="y*8i&l0^b)%l4ymt631e69=78!4uh!=iity6e-c%m2n&2aepxr",
        DATABASES={
            "default": {
                "NAME": ":memory:",
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sessions",
            "conditions",
            "tests",
        ),
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ]
                },
            }
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        ROOT_URLCONF="tests.urls",
    )
    django.setup()
    call_command("test")
