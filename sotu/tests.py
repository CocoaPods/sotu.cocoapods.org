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

    def test_with_invitation(self):
        entrant = Entrant.create(email='kyle@cocoapods.org', name='Kyle', github_username='kylef')
        invitation = entrant.invite()
        invitation.save()

        response = self.client.get('/callback', {'code': 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://sotu.cocoapods.org/invitation/{}'.format(invitation.code))

        entrant.delete_instance()
        invitation.delete_instance()

    def test_with_rejected_invitation(self):
        entrant = Entrant.create(email='kyle@cocoapods.org', name='Kyle', github_username='kylef')
        invitation = entrant.invite()
        invitation.state = Invitation.REJECTED_STATE
        invitation.save()

        response = self.client.get('/callback', {'code': 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://sotu.cocoapods.org/invitation/{}/reject'.format(invitation.code))

        entrant.delete_instance()
        invitation.delete_instance()

    def test_with_accepted_invitation(self):
        entrant = Entrant.create(email='kyle@cocoapods.org', name='Kyle', github_username='kylef')
        invitation = entrant.invite()
        invitation.state = Invitation.ACCEPTED_STATE
        invitation.save()

        response = self.client.get('/callback', {'code': 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://sotu.cocoapods.org/invitation/{}/accept'.format(invitation.code))

        entrant.delete_instance()
        invitation.delete_instance()


class InvitationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(middleware)
        self.entrant = Entrant.create(email='kyle@cocoapods.org', name='Kyle', github_username='kylef')
        self.invitation = self.entrant.invite()
        self.path = '/invitation/{}'.format(self.invitation.code)

    def tearDown(self):
        self.entrant.delete_instance()
        self.invitation.delete_instance()

    def get_invitation(self):
        return self.entrant.invitation_set.get()

    def assertState(self, state):
        self.assertEqual(self.get_invitation().state, state)


class InvitedTests(InvitationTests):
    def test_invited(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)


class RejectInvitationTests(InvitationTests):
    def test_rejecting_invite(self):
        response = self.client.get(self.path + '/reject')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.REJECTED_STATE)

    def test_rejecting_accepted_invite(self):
        self.invitation.state = Invitation.ACCEPTED_STATE
        self.invitation.save()

        response = self.client.get(self.path + '/reject')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.REJECTED_STATE)


class AcceptInvitationTests(InvitationTests):
    def test_accepting_invite(self):
        response = self.client.get(self.path + '/accept')
        self.assertEqual(response.status_code, 200)
        self.assertState(Invitation.ACCEPTED_STATE)

    def test_accepting_rejected_invite(self):
        self.invitation.state = Invitation.REJECTED_STATE
        self.invitation.save()

        with self.assertRaises(Http404):
            self.client.get(self.path + '/accept')

    def test_cant_accept_invite_with_max_attendees(self):
        def create_entrant(number):
            return Entrant.create(email='kyle_{}@cocoapods.org'.format(number),
                    name='Kyle', github_username='kylef_{}'.format(number))

        def accept_entrant(entrant):
            invitation = entrant.invite()
            invitation.state = Invitation.ACCEPTED_STATE
            invitation.save()
            return invitation

        entrants = map(create_entrant, range(0, 185))
        invitations = map(accept_entrant, entrants)

        response = self.client.get(self.path + '/accept')
        self.assertEqual(response.status_code, 302)

        for invitation in invitations:
            invitation.delete_instance()

        for entrant in entrants:
            entrant.delete_instance()
