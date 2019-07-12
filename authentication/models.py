from django.contrib.auth.models import User
from django.db import models

from authentication.managers import PersonManager


class Person(User):
    objects = PersonManager()

    class Meta:
        proxy = True