import datetime
from django.test import TestCase, Client
from account.models import User, Profile, ResetPasswordRequest
from django.contrib.auth.hashers import check_password, make_password


class TestRegister(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_already_exists = User.objects.create(
            username="first",
            email="first@f.f",
            password="123" # its not hashed but it's not important. don't worry about it :)
        )

    def test_register_request_without_some_fields_will_not_work(self):
        self.assertEqual(self.client.post('/account/register/', {'email': "a@a.a", "password": "123"}).status_code, 400)
        self.assertEqual(self.client.post('/account/register/', {'username': "a", "password": "123"}).status_code, 400)
        self.assertEqual(self.client.post('/account/register/', {'email': "a@a.a", "username": "a"}).status_code, 400)
        self.assertEqual(self.client.post('/account/register/', {}).status_code, 400)

        self.assertEqual(self.client.post('/account/register/', {'email': "a"*300}).status_code, 400)
        self.assertEqual(self.client.post('/account/register/', {'username': "a"*300}).status_code, 400)
        self.assertEqual(self.client.post('/account/register/', {'username': 'a'*300, 'email': "a"*300}).status_code, 400)

    def test_user_cannot_be_registered_with_repeated_username_or_password(self):
        res = self.client.post('/account/register/', {
            "username": "first",
            "email": "foo@f.f",
            "password": "335",
        })
        self.assertEqual(res.status_code, 409)
        self.assertEqual(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "second",
            "email": "first@f.f",
            "password": "335",
        })
        self.assertEqual(res.status_code, 409)
        self.assertEqual(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "first",
            "email": "first@f.f",
            "password": "335",
        })
        self.assertEqual(res.status_code, 409)
        self.assertEqual(User.objects.all().count(), 1)

        res = self.client.post('/account/register/', {
            "username": "new",
            "email": "new@n.n",
            "password": "123",
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(User.objects.all().count(), 2)
        created_user = User.objects.filter(username="new", email="new@n.n").get()
        self.assertNotEquals(created_user, None)
        self.assertEqual(res.json()['api_token'], created_user.profile.api_token)
        self.assertTrue(check_password('123', created_user.password))


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
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'password': '123'})
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'email': 'a@a.a'})
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'a'})
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'a', 'email': 'a@a.a'})
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/get-token/', {'username': 'u1', 'password': '123'})
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/account/get-token/', {'username': 'u', 'password': '1234'})
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/account/get-token/', {'username': 'u', 'password': '123'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['token'], self.user.profile.api_token)

    def test_user_can_ask_who_they_are(self):
        res = self.client.get('/account/whoami/', HTTP_TOKEN='something')
        self.assertEqual(res.status_code, 401)
        res = self.client.get('/account/whoami/')
        self.assertEqual(res.status_code, 401)

        token = self.user.profile.api_token
        res = self.client.get('/account/whoami/', HTTP_TOKEN=token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {'user': self.user.profile.to_json()})

    def test_user_can_reset_their_token(self):
        res = self.client.post('/account/reset-token/', HTTP_TOKEN='something')
        self.assertEqual(res.status_code, 401)
        res = self.client.post('/account/reset-token/')
        self.assertEqual(res.status_code, 401)

        token = self.user.profile.api_token
        res = self.client.post('/account/reset-token/', HTTP_TOKEN=token)
        self.assertEqual(res.status_code, 200)
        new_token = res.json()['new_token']
        self.assertNotEquals(token, new_token)

    def test_reset_password_works(self):
        res = self.client.post('/account/reset-password/')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/reset-password/', {'username': 'somethingnotfound'})
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/account/reset-password/', {'email': 'something@not.found'})
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/account/reset-password/', {'email': self.user.email})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(ResetPasswordRequest.objects.filter(user=self.user).exists())
        req = ResetPasswordRequest.objects.filter(user=self.user).first()
        expires_at = req.expires_at

        res = self.client.post('/account/reset-password/', {'username': self.user.username})
        self.assertEqual(res.status_code, 200)
        req2 = ResetPasswordRequest.objects.filter(user=self.user).first()
        expires_at2 = req2.expires_at

        self.assertEqual(expires_at, expires_at2)
        self.assertEqual(req.id, req2.id)

        # let's make request expired
        req.expires_at = expires_at - datetime.timedelta(hours=4)
        req.save()

        res = self.client.post('/account/reset-password/', {'username': self.user.username})
        self.assertEqual(res.status_code, 200)

        try:
            req.refresh_from_db()
            self.assertTrue(false)
        except:
            pass

        req = ResetPasswordRequest.objects.filter(user=self.user).first()
        req.expires_at = expires_at - datetime.timedelta(hours=4)
        req.save()

        res = self.client.post('/account/reset-password-final/')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/account/reset-password-final/', {'code': 'wrongshit'})
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/account/reset-password-final/', {'code': req.code})
        self.assertEqual(res.status_code, 403)

        req.expires_at = expires_at + datetime.timedelta(hours=4)
        req.save()

        res = self.client.post('/account/reset-password-final/', {'code': req.code})
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/account/reset-password-final/', {'code': req.code, 'new_password': 'ThisIsMyNewPassword'})
        self.assertEqual(res.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(check_password('ThisIsMyNewPassword', self.user.password))

        try:
            req.refresh_from_db()
            self.assertTrue(False)
        except:
            pass
