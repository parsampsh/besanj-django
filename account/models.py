from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Profile(models.Model):
    """ Additional data for the User model """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_token = models.CharField(max_length=70, unique=True) # A token for accessing to the API

    @staticmethod
    def generate_unique_token():
        token = get_random_string(70)

        while Profile.objects.filter(api_token=token).exists():
            token = get_random_string(70)

        return token
