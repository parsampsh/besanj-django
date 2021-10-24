from django.test import TestCase, Client
from polls.models import *
from account.models import Profile


class TestPollsCrud(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User(username="a", email="a@a.a", password='123')
        self.user.save()
        Profile(user=self.user, api_token='test').save()

    def test_poll_cannot_be_created_without_valid_information(self):
        self.assertEquals(
            self.client.post('/polls/create/', {}).status_code,
            401
        )

        self.assertEquals(
            self.client.post('/polls/create/', {'description': 'hi'}, HTTP_TOKEN='test').status_code,
            400
        )
        self.assertEquals(
            self.client.post('/polls/create/', {}, HTTP_TOKEN='test').status_code,
            400
        )
        self.assertEquals(
            self.client.post('/polls/create/', {'title': 'a'*300}, HTTP_TOKEN='test').status_code,
            400
        )
        self.assertEquals(
            self.client.post('/polls/create/', {'description': 'a'*300}, HTTP_TOKEN='test').status_code,
            400
        )
        self.assertEquals(
            self.client.post('/polls/create/', {'title': 'hi', 'description': 'a'*1500}, HTTP_TOKEN='test').status_code,
            400
        )
        self.assertEquals(
            self.client.post('/polls/create/', {'description': 'hi', 'title': 'a'*300}, HTTP_TOKEN='test').status_code,
            400
        )

    def test_poll_can_be_created(self):
        res = self.client.post('/polls/create/', {
            'title': 'The Title',
            'description': 'The Description',
        }, HTTP_TOKEN='test')
        created_poll_id = res.json()['created_poll_id']
        created_poll = Poll.objects.get(pk=created_poll_id)

        self.assertEquals(created_poll.title, 'The Title')
        self.assertEquals(created_poll.description, 'The Description')
        self.assertEquals(created_poll.is_published, False)
        self.assertEquals(created_poll.user.id, self.user.id)

        res = self.client.post('/polls/create/', {
            'title': 'The Title',
        }, HTTP_TOKEN='test')
        created_poll_id = res.json()['created_poll_id']
        created_poll = Poll.objects.get(pk=created_poll_id)

        self.assertEquals(created_poll.title, 'The Title')
        self.assertEquals(created_poll.description, None)
        self.assertEquals(created_poll.is_published, False)
        self.assertEquals(created_poll.user.id, self.user.id)
