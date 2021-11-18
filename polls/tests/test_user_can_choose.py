from django.test import TestCase, Client
from polls.models import *
from account.models import Profile


class TestUserCanChoose(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User(username='a', email='a@a.a', password='123')
        self.user.save()
        profile = Profile(user=self.user, api_token='test')
        profile.save()

        self.poll = Poll(title='test poll', user=self.user)
        self.poll.save()

        self.choices = [
            Choice.objects.create(poll=self.poll, title='a', sort=1),
            Choice.objects.create(poll=self.poll, title='b', sort=2),
            Choice.objects.create(poll=self.poll, title='c', sort=3),
        ]

    def test_user_cannot_select_a_choice_with_invalid_information(self):
        self.assertEqual(self.client.post('/polls/choose/', {}).status_code, 401)
        self.assertEqual(self.client.post('/polls/choose/', {}, HTTP_TOKEN='test').status_code, 404)
        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': 12345}, HTTP_TOKEN='test').status_code, 404)
        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[0].id}, HTTP_TOKEN='test').status_code, 403)
        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[1].id}, HTTP_TOKEN='test').status_code, 403)
        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[2].id}, HTTP_TOKEN='test').status_code, 403)

    def test_user_can_select_a_choice(self):
        self.poll.is_published = True
        self.poll.save()

        self.assertFalse(self.choices[0].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[1].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[2].users.filter(pk=self.user.id).exists())

        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[2].id}, HTTP_TOKEN='test').status_code, 200)

        self.assertFalse(self.choices[0].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[1].users.filter(pk=self.user.id).exists())
        self.assertTrue(self.choices[2].users.filter(pk=self.user.id).exists())

        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[0].id}, HTTP_TOKEN='test').status_code, 200)

        self.assertTrue(self.choices[0].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[1].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[2].users.filter(pk=self.user.id).exists())

        self.assertEqual(self.client.post('/polls/choose/', {'choice_id': self.choices[0].id}, HTTP_TOKEN='test').status_code, 200)

        self.assertFalse(self.choices[0].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[1].users.filter(pk=self.user.id).exists())
        self.assertFalse(self.choices[2].users.filter(pk=self.user.id).exists())
