import unittest

from rivr.tests import TestClient
from rivr.http import Http404
from sotu.middleware import middleware
from sotu.models import Entrant, Invitation


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
        entrant.delete_instance()


class InvitationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(middleware)
        self.entrant = Entrant.create(email='kyle@cocoapods.org', name='Kyle', github_username='kylef')
        self.invitation = self.entrant.invite()
        self.path = '/invitation/{}/'.format(self.invitation.code)

    def tearDown(self):
        self.entrant.delete_instance()
        self.invitation.delete_instance()

    def get_invitation(self):
        return self.entrant.invitation_set.get()

    def assertState(self, state):
        self.assertEqual(self.get_invitation().state, state)


class RejectInvitationTests(InvitationTests):
    def test_rejecting_invite(self):
        response = self.client.get(self.path + 'reject')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.REJECTED_STATE)

    def test_rejecting_accepted_invite(self):
        self.invitation.state = Invitation.ACCEPTED_STATE
        self.invitation.save()

        response = self.client.get(self.path + 'reject')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.REJECTED_STATE)


class AcceptInvitationTests(InvitationTests):
    def test_accepting_invite(self):
        response = self.client.get(self.path + 'accept')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.ACCEPTED_STATE)

    def test_accepting_rejected_invite(self):
        self.invitation.state = Invitation.REJECTED_STATE
        self.invitation.save()

        with self.assertRaises(Http404):
            self.client.get(self.path + 'accept')

