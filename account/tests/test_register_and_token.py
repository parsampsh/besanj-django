from django.test import TestCase, Client
from account.models import User
from django.contrib.auth.hashers import check_password


class TestRegisterAndToken(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_already_exists = User.objects.create(
            username="first",
            email="first@f.f",
            password="123" # its not hashed but it's not important. don't worry about it :)
        )

    def test_register_request_without_some_fields_will_not_work(self):
        self.assertEquals(self.client.post('/account/register/', {'email': "a@a.a", "password": "123"}).status_code, 400)
        self.assertEquals(self.client.post('/account/register/', {'username': "a", "password": "123"}).status_code, 400)
        self.assertEquals(self.client.post('/account/register/', {'email': "a@a.a", "username": "a"}).status_code, 400)
        self.assertEquals(self.client.post('/account/register/', {}).status_code, 400)

    def test_user_cannot_be_registered_with_repeated_username_or_password(self):
        res = self.client.post('/account/register/', {
            "username": "first",
            "email": "foo@f.f",
            "password": "335",
        })
        self.assertEquals(res.status_code, 409)
        self.assertEquals(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "second",
            "email": "first@f.f",
            "password": "335",
        })
        self.assertEquals(res.status_code, 409)
        self.assertEquals(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "first",
            "email": "first@f.f",
            "password": "335",
        })
        self.assertEquals(res.status_code, 409)
        self.assertEquals(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "new",
            "email": "new@n.n",
            "password": "123",
        })
        self.assertEquals(res.status_code, 201)
        self.assertEquals(User.objects.all().count(), 2)
        created_user = User.objects.filter(username="new", email="new@n.n").get()
        self.assertNotEquals(created_user, None)
        self.assertEquals(res.json()['api_token'], created_user.profile.api_token)
        self.assertTrue(check_password('123', created_user.password))
