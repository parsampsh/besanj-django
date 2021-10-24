from django.test import TestCase, Client
from polls.models import *
from account.models import Profile


class TestPollsManagement(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User(username="a", email="a@a.a", password='123')
        self.user.save()
        Profile(user=self.user, api_token='test').save()

        self.user2 = User(username="b", email="b@a.a", password='123')
        self.user2.save()
        Profile(user=self.user2, api_token='test2').save()

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

    def test_poll_can_be_deleted(self):
        poll = Poll(title='hello', user=self.user2)
        poll.save()

        self.assertEquals(self.client.post('/polls/delete/', {}).status_code, 401)
        self.assertEquals(self.client.post('/polls/delete/', {}, HTTP_TOKEN='test').status_code, 404)
        self.assertEquals(self.client.post('/polls/delete/', {'poll_id': 12356}, HTTP_TOKEN='test').status_code, 404)
        self.assertEquals(self.client.post('/polls/delete/', {'poll_id': poll.id}, HTTP_TOKEN='test').status_code, 403)

        self.assertEquals(self.client.post('/polls/delete/', {'poll_id': poll.id}, HTTP_TOKEN='test2').status_code, 200)

        poll_id = poll.id
        self.assertFalse(Poll.objects.filter(pk=poll_id).exists())
