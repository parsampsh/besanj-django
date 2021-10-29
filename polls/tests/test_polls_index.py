from django.test import TestCase, Client
from polls.models import *
from account.models import Profile


class TestPollsIndex(TestCase):
    def setUp(self):
        self.client = Client()

        self.user1 = User(username="a", password='123')
        self.user1.save()
        self.user1.profile = Profile(api_token='1')
        self.user1.profile.save()

        self.user2 = User(username="b", password='123')
        self.user2.save()
        self.user2.profile = Profile(api_token='2')
        self.user2.profile.save()

        for i in range(0, 350):
            if i < 150:
                u = self.user1
            else:
                u = self.user2
            poll = Poll(title='poll ' + str(i), user=u, description='the description')
            if i % 2 == 0:
                poll.is_published = True
            poll.save()

            for j in range(0, 4):
                choice = Choice(title='choice ' + str(j), poll=poll, sort=j)
                choice.save()

    def test_polls_will_be_shown_for_a_specific_user(self):
        res = self.client.get('/polls/?user_id=123456')
        self.assertEquals(res.status_code, 404)

        res = self.client.get('/polls/?user_id=' + str(self.user1.id))
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 75)
        self.assertEquals(res_json['pages_count'], 2)
        self.assertEquals(res_json['current_page'], 1)
        self.assertEquals(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=2&user_id=' + str(self.user1.id))
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 75)
        self.assertEquals(res_json['pages_count'], 2)
        self.assertEquals(res_json['current_page'], 2)
        self.assertEquals(len(res_json['polls']), 25)

        res = self.client.get('/polls/?user_id=' + str(self.user2.id))
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 100)
        self.assertEquals(res_json['pages_count'], 2)
        self.assertEquals(res_json['current_page'], 1)
        self.assertEquals(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=2&user_id=' + str(self.user2.id))
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 100)
        self.assertEquals(res_json['pages_count'], 2)
        self.assertEquals(res_json['current_page'], 2)
        self.assertEquals(len(res_json['polls']), 50)

        res = self.client.get('/polls/?user_id=' + str(self.user2.id), HTTP_TOKEN='invalid')
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 100)
        self.assertEquals(res_json['pages_count'], 2)
        self.assertEquals(res_json['current_page'], 1)
        self.assertEquals(len(res_json['polls']), 50)

        res = self.client.get('/polls/?user_id=' + str(self.user2.id), HTTP_TOKEN=self.user2.profile.api_token)
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 200)
        self.assertEquals(res_json['pages_count'], 4)
        self.assertEquals(res_json['current_page'], 1)
        self.assertEquals(len(res_json['polls']), 50)

    def test_single_poll_can_be_shown(self):
        poll1 = self.user1.poll_set.all()[0]
        poll1.is_published = False
        poll1.save()
        poll2 = self.user1.poll_set.all()[1]
        poll2.is_published = True
        poll2.save()

        res = self.client.get('/polls/?single_poll_id=' + str(poll2.id))
        self.assertEquals(res.json()['polls'][0]['title'], poll2.title)

        res = self.client.get('/polls/?single_poll_id=123456')
        self.assertEquals(res.status_code, 404)

        res = self.client.get('/polls/?single_poll_id=' + str(poll1.id))
        self.assertEquals(res.status_code, 404)

    def test_polls_index_works_correctly(self):
        res = self.client.get('/polls/')
        self.assertEquals(res.status_code, 200)
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 175)
        self.assertEquals(res_json['pages_count'], 4)
        self.assertEquals(res_json['current_page'], 1)
        self.assertEquals(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=4')
        self.assertEquals(res.status_code, 200)
        res_json = res.json()
        self.assertEquals(res_json['all_count'], 175)
        self.assertEquals(res_json['pages_count'], 4)
        self.assertEquals(res_json['current_page'], 4)
        self.assertEquals(len(res_json['polls']), 25)

    def test_single_poll_json_data(self):
        poll = self.user1.poll_set.all()[1]
        poll.is_published = True
        poll.save()
        choice = poll.choice_set.all()[0]
        choice.users.add(self.user2)

        res = self.client.get('/polls/?single_poll_id=' + str(poll.id))
        poll_json = res.json()['polls'][0]

        self.assertEquals(poll_json['id'], poll.id)
        self.assertEquals(poll_json['title'], poll.title)
        self.assertEquals(poll_json['description'], poll.description)
        self.assertEquals(poll_json['is_published'], True)
        self.assertEquals(poll_json['created_at'], str(poll.created_at))
        self.assertEquals(poll_json['user']['username'], poll.user.username)
        self.assertEquals(poll_json['user']['email'], poll.user.email)

        self.assertEquals(poll_json['choices'][0]['id'], choice.id)
        self.assertEquals(poll_json['choices'][0]['title'], choice.title)
        self.assertEquals(poll_json['choices'][0]['sort'], choice.sort)

        self.assertEquals(poll_json['choices'][0]['votes_count'], 1)
        self.assertEquals(poll_json['choices'][0]['votes_percent'], 100)

    def test_search_works_correctly(self):
        res = self.client.get('/polls/?search=poll')
        self.assertEquals(res.json()['all_count'], 175)

        res = self.client.get('/polls/?search=ol')
        self.assertEquals(res.json()['all_count'], 175)

        res = self.client.get('/polls/?search=hello')
        self.assertEquals(res.json()['all_count'], 0)

        res = self.client.get('/polls/?search=the des')
        self.assertEquals(res.json()['all_count'], 175)
