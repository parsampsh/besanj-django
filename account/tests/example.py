from django.test import TestCase, Client


class TestName(TestCase):
    def setUp(self):
        self.client = Client()
