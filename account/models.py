from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """ Additional data for the User model """
    user = models.OneToOneField(User)
    api_token = models.CharField(max_length=70) # A token for accessing to the API
