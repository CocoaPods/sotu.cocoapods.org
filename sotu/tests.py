tasks.pyimport unittest
from rivr.tests import TestClient
from sotu.middleware import middleware


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(middleware)

    def test_index_links_to_github_authorization(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('https://github.com/login/oauth/authorize' in response.content)

