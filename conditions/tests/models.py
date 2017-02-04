from django.contrib.auth.models import User
from django.db import models

from ..fields import ConditionsField
from ..types import conditions_from_module
from . import conditions


class UserProfile(models.Model):

    user = models.OneToOneField(User)
    level = models.IntegerField(default=1)


class Campaign(models.Model):

    text = models.TextField()
    conditions = ConditionsField(definitions=conditions_from_module(conditions))
