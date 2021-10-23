from django.test import TestCase, Client
from account.models import User, Profile
from django.contrib.auth.hashers import make_password


class TestToken(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="u", email="u@u.u", password=make_password("123"))
        p = Profile()
        p.user = self.user
        p.api_token = 'i-am-token'
        p.save()

    def test_user_cannot_get_token_with_wrong_information(self):
        res = self.client.post('/account/get-token/', {})
        self.assertEquals(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'password': '123'})
        self.assertEquals(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'email': 'a@a.a'})
        self.assertEquals(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'a'})
        self.assertEquals(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'a', 'email': 'a@a.a'})
        self.assertEquals(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'u1', 'password': '123'})
        self.assertEquals(res.status_code, 401)

        res = self.client.post('/account/get-token/', {'username': 'u', 'password': '1234'})
        self.assertEquals(res.status_code, 401)

        res = self.client.post('/account/get-token/', {'username': 'u', 'password': '123'})
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.json()['token'], self.user.profile.api_token)

    def test_user_can_ask_who_they_are(self):
        res = self.client.get('/account/whoami/', HTTP_TOKEN='something')
        self.assertEquals(res.status_code, 401)
        res = self.client.get('/account/whoami/')
        self.assertEquals(res.status_code, 401)

        token = self.user.profile.api_token
        res = self.client.get('/account/whoami/', HTTP_TOKEN=token)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.json(), {'user': self.user.profile.to_json()})

    def test_user_can_reset_their_token(self):
        res = self.client.post('/account/reset-token/', HTTP_TOKEN='something')
        self.assertEquals(res.status_code, 401)
        res = self.client.post('/account/reset-token/')
        self.assertEquals(res.status_code, 401)

        token = self.user.profile.api_token
        res = self.client.post('/account/reset-token/', HTTP_TOKEN=token)
        self.assertEquals(res.status_code, 200)
        new_token = res.json()['new_token']
        self.assertNotEquals(token, new_token)
