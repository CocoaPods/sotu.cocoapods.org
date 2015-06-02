import unittest

from rivr.tests import TestClient
from sotu.middleware import middleware
from sotu.models import Entrant


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(middleware)

    def test_index_links_to_github_authorization(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('https://github.com/login/oauth/authorize' in response.content)


class GitHubCallbackTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(middleware)

    def test_successfully_authenticates_user_from_github(self):
        response = self.client.get('/callback', {'code': 5})
        self.assertEqual(response.status_code, 200)
        entrant = Entrant.select().where(Entrant.email == 'kyle@cocoapods.org').get()
        self.assertEqual(entrant.name, 'kylef')

