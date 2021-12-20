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
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/polls/?user_id=' + str(self.user1.id))
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 75)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=2&user_id=' + str(self.user1.id))
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 75)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 2)
        self.assertEqual(len(res_json['polls']), 25)

        res = self.client.get('/polls/?user_id=' + str(self.user2.id))
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 100)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=2&user_id=' + str(self.user2.id))
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 100)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 2)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/?user_id=' + str(self.user2.id), HTTP_TOKEN='invalid')
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 100)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)
        self.assertFalse(res_json['polls'][0]['belongs_to_you'])

        res = self.client.get('/polls/?user_id=' + str(self.user2.id), HTTP_TOKEN=self.user2.profile.api_token)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 200)
        self.assertEqual(res_json['pages_count'], 4)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)
        self.assertTrue(res_json['polls'][0]['belongs_to_you'])

    def test_single_poll_can_be_shown(self):
        poll1 = self.user1.poll_set.all()[0]
        poll1.is_published = False
        poll1.save()
        poll2 = self.user1.poll_set.all()[1]
        poll2.is_published = True
        poll2.save()

        res = self.client.get('/polls/?single_poll_id=' + str(poll2.id))
        self.assertEqual(res.json()['polls'][0]['title'], poll2.title)

        res = self.client.get('/polls/?single_poll_id=123456')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/polls/?single_poll_id=' + str(poll1.id))
        self.assertEqual(res.status_code, 404)

    def test_polls_index_works_correctly(self):
        res = self.client.get('/polls/')
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 175)
        self.assertEqual(res_json['pages_count'], 4)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/?page=4')
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 175)
        self.assertEqual(res_json['pages_count'], 4)
        self.assertEqual(res_json['current_page'], 4)
        self.assertEqual(len(res_json['polls']), 25)

    def test_single_poll_json_data(self):
        poll = self.user1.poll_set.all()[1]
        poll.is_published = True
        poll.save()
        choice = poll.choice_set.all()[0]
        choice.users.add(self.user2)

        res = self.client.get('/polls/?single_poll_id=' + str(poll.id))
        poll_json = res.json()['polls'][0]

        self.assertEqual(poll_json['id'], poll.id)
        self.assertEqual(poll_json['title'], poll.title)
        self.assertEqual(poll_json['description'], poll.description)
        self.assertEqual(poll_json['is_published'], True)
        self.assertEqual(poll_json['created_at'], str(poll.created_at))
        self.assertEqual(poll_json['user']['username'], poll.user.username)
        self.assertEqual(poll_json['user']['email'], poll.user.email)

        self.assertEqual(poll_json['choices'][0]['id'], choice.id)
        self.assertEqual(poll_json['choices'][0]['title'], choice.title)
        self.assertEqual(poll_json['choices'][0]['sort'], choice.sort)

        self.assertEqual(poll_json['choices'][0]['votes_count'], 1)
        self.assertEqual(poll_json['choices'][0]['votes_percent'], 100)

    def test_search_works_correctly(self):
        res = self.client.get('/polls/?search=poll')
        self.assertEqual(res.json()['all_count'], 175)

        res = self.client.get('/polls/?search=ol')
        self.assertEqual(res.json()['all_count'], 175)

        res = self.client.get('/polls/?search=hello')
        self.assertEqual(res.json()['all_count'], 0)

        res = self.client.get('/polls/?search=the des')
        self.assertEqual(res.json()['all_count'], 175)

    def test_user_can_see_their_votes(self):
        res = self.client.get('/polls/my_votes/')
        self.assertEqual(res.status_code, 401)

        res = self.client.get('/polls/my_votes/', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 0)
        self.assertEqual(res_json['pages_count'], 1)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 0)

        polls = self.user2.poll_set.filter(is_published=True).all()[0:80]
        for poll in polls:
            poll.choice_set.all()[0].users.add(self.user1)

        res = self.client.get('/polls/my_votes/', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 80)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/my_votes/?search=320', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 0)
        self.assertEqual(res_json['pages_count'], 1)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 0)

        res = self.client.get('/polls/my_votes/?search=308', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 1)
        self.assertEqual(res_json['pages_count'], 1)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 1)
        self.assertEqual(res_json['polls'][0]['title'], 'poll 308')

        res = self.client.get('/polls/my_votes/?page=gfdg', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 80)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 1)
        self.assertEqual(len(res_json['polls']), 50)

        res = self.client.get('/polls/my_votes/?page=2', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 80)
        self.assertEqual(res_json['pages_count'], 2)
        self.assertEqual(res_json['current_page'], 2)
        self.assertEqual(len(res_json['polls']), 30)
        self.assertTrue('selected_choice' in res_json['polls'][0])

        self.user1.choice_set.clear()
        polls = Poll.objects.order_by('-created_at').filter(is_published=True).all()[0:80]
        for poll in polls:
            poll.choice_set.all()[0].users.add(self.user1)

        res = self.client.get('/polls/?page=2', HTTP_TOKEN=self.user1.profile.api_token)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(res_json['all_count'], 175)
        self.assertEqual(res_json['pages_count'], 4)
        self.assertEqual(res_json['current_page'], 2)
        self.assertEqual(len(res_json['polls']), 50)
        self.assertTrue('selected_choice' in res_json['polls'][0])
        self.assertFalse('selected_choice' in res_json['polls'][40])
