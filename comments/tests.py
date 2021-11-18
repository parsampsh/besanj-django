from django.test import TestCase, Client
from .models import *
from account.models import Profile


class TestCommentCreation(TestCase):
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

        self.poll1 = Poll.objects.create(title='a', user=self.user1, description='a', is_published=True)
        self.poll2 = Poll.objects.create(title='b', user=self.user1, description='b', is_published=True)
        self.poll3 = Poll.objects.create(title='c', user=self.user1, description='c', is_published=False)

        self.comment1 = Comment.objects.create(user=self.user2, poll=self.poll1, text="test", is_published=True)
        self.comment2 = Comment.objects.create(user=self.user2, poll=self.poll1, text="hi", is_published=False)

    def test_user_cannot_send_comment_without_authentication(self):
        res = self.client.post('/comments/send/')
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/comments/send/', HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/comments/send/', {'poll_id': 123}, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/comments/send/', {'text': 'test'}, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 400)

    def test_comment_cannot_be_sent_on_wrong_poll(self):
        res = self.client.post('/comments/send/', {'text': 'test', 'poll_id': 12345}, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/comments/send/', {'text': 'test', 'poll_id': self.poll3.id}, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 404)

    def test_comment_cannot_be_sent_on_wrong_parent_comment(self):
        res = self.client.post('/comments/send/', {
            'text': 'test',
            'poll_id': self.poll2.id,
            'parent_comment_id': 12345
        }, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/comments/send/', {
            'text': 'test',
            'poll_id': self.poll2.id,
            'parent_comment_id': self.comment2.id
        }, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 404)

    def test_comment_can_be_sent(self):
        res = self.client.post('/comments/send/', {
            'text': 'a' * 600,
            'poll_id': self.poll2.id,
            'parent_comment_id': self.comment1.id
        }, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/comments/send/', {
            'text': 'created',
            'poll_id': self.poll2.id,
            'parent_comment_id': self.comment1.id
        }, HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 201)
        res_json = res.json()['created_comment']

        created_comment = Comment.objects.filter(text='created', poll=self.poll2, parent_comment=self.comment1).get()
        self.assertEqual(created_comment.user.id, self.user2.id)

        self.assertEqual(res_json['id'], created_comment.id)
        self.assertEqual(res_json['poll_id'], created_comment.poll.id)
        self.assertEqual(res_json['parent_comment_id'], created_comment.parent_comment.id)
        self.assertEqual(res_json['user']['email'], created_comment.user.email)
        self.assertEqual(res_json['is_published'], created_comment.is_published)

        res = self.client.post('/comments/send/', {
            'text': 'sent',
            'poll_id': self.poll1.id,
        }, HTTP_TOKEN='1')
        self.assertEqual(res.status_code, 201)
        res_json = res.json()['created_comment']

        created_comment = Comment.objects.filter(text='sent', poll=self.poll1, parent_comment=None).get()
        self.assertEqual(created_comment.user.id, self.user1.id)

        self.assertEqual(res_json['id'], created_comment.id)
        self.assertEqual(res_json['poll_id'], created_comment.poll.id)
        self.assertEqual(res_json['user']['email'], created_comment.user.email)
        self.assertEqual(res_json['is_published'], created_comment.is_published)
        self.assertTrue('parent_comment_id' not in res_json)


class TestCommentDeletion(TestCase):
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

        self.poll1 = Poll.objects.create(title='a', user=self.user1, description='a', is_published=True)

        self.comment1 = Comment.objects.create(user=self.user1, poll=self.poll1, text="test", is_published=True)
        self.comment2 = Comment.objects.create(user=self.user2, poll=self.poll1, text="hi", is_published=True)

    def test_user_cannot_delete_comment_without_authentication(self):
        res = self.client.post('/comments/delete/')
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/comments/delete/', HTTP_TOKEN='1')
        self.assertEqual(res.status_code, 404)

        res = self.client.post('/comments/delete/', {'comment_id': 12345}, HTTP_TOKEN='1')
        self.assertEqual(res.status_code, 404)

    def test_user_cannot_delete_comment_of_other_user(self):
        res = self.client.post('/comments/delete/', {'comment_id': self.comment2.id}, HTTP_TOKEN='1')
        self.assertEqual(res.status_code, 403)

    def test_user_can_delete_comment(self):
        res = self.client.post('/comments/delete/', {'comment_id': self.comment1.id}, HTTP_TOKEN='1')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=self.comment1.id).exists())


class TestCommentsList(TestCase):
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

        self.poll1 = Poll.objects.create(title='a', user=self.user1, description='a', is_published=True)

        self.comment1 = Comment.objects.create(user=self.user1, poll=self.poll1, text="a", is_published=True)
        self.comment2 = Comment.objects.create(user=self.user1, poll=self.poll1, text="b", is_published=True)
        self.comment3 = Comment.objects.create(user=self.user1, poll=self.poll1, text="c", is_published=True)
        self.comment4 = Comment.objects.create(user=self.user2, poll=self.poll1, text="1", is_published=True)
        self.comment5 = Comment.objects.create(user=self.user2, poll=self.poll1, text="2", is_published=True)
        self.comment6 = Comment.objects.create(user=self.user2, poll=self.poll1, text="3", is_published=False)

    def test_comments_by_user_will_be_returned_correctly(self):
        res = self.client.get('/comments/user_comments/')
        self.assertEqual(res.status_code, 400)

        res = self.client.get('/comments/user_comments/?user_id=123456')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/comments/user_comments/?user_id=' + str(self.user2.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()['comments']), 2)

        res = self.client.get('/comments/user_comments/?user_id=' + str(self.user2.id), HTTP_TOKEN='2')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()['comments']), 3)

        self.assertEqual(res.json()['all_count'], 3)
        self.assertEqual(res.json()['pages_count'], 1)
        self.assertEqual(res.json()['current_page'], 1)

    def test_comments_by_poll_will_be_returned_correctly(self):
        res = self.client.get('/comments/poll_comments/')
        self.assertEqual(res.status_code, 400)

        res = self.client.get('/comments/poll_comments/?poll_id=123456')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/comments/poll_comments/?poll_id=' + str(self.poll1.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()['comments']), 5)

        self.assertEqual(res.json()['comments'][0]['id'], self.comment5.id)
