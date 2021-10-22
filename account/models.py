from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Profile(models.Model):
    """ Additional data for the User model """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_token = models.CharField(max_length=70, unique=True) # A token for accessing to the API

    def to_json(self):
        """ Returns the user information in the json format """
        return {
            'username': self.user.username,
            'email': self.user.email,
        }

    @staticmethod
    def generate_unique_token():
        """ Generates a new unique random token for api_token field """
        token = get_random_string(70)

        while Profile.objects.filter(api_token=token).exists():
            token = get_random_string(70)

        return token
