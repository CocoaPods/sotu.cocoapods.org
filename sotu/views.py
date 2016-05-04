import json

from rivr import Http404
from rivr.http import Response, ResponseRedirect
from rivr_jinja import JinjaView, JinjaResponse

from sotu.github import *
from sotu.models import Entrant, Invitation


ATTENDEE_LIMIT = 185


class IndexView(JinjaView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        parameters = {
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': GITHUB_CALLBACK_URI,
            'scope': 'user:email',
            'state': 'unused',
        }

        return {
            'github_authorize_uri': 'https://github.com/login/oauth/authorize?' + urllib.urlencode(parameters)
        }


class EntrantView(JinjaView):
    template_name = 'entrant.html'

    def get_context_data(self, **kwargs):
        return {
            'entrant': self.entrant,
            'avatar': self.avatar,
        }


class InvitationView(JinjaView):
    template_name = 'invited.html'
    expected_states = (Invitation.INVITED_STATE,)
    enforce_attendee_limit = True

    @property
    def has_reached_limit(self):
        attendees = Invitation.select().where(Invitation.state == Invitation.ACCEPTED_STATE).count()
        return attendees >= ATTENDEE_LIMIT

    def get_context_data(self, **kwargs):
        return {
            'invitation': self.invitation,
            'entrant': self.invitation.entrant,
        }

    def perform(self, invitation):
        pass

    def get(self, *args, **kwargs):
        try:
            self.invitation = Invitation.select().where(Invitation.code == kwargs['code']).get()
        except Invitation.DoesNotExist:
            raise Http404

        if self.invitation.state not in self.expected_states:
            raise Http404

        if self.invitation.state == Invitation.REMOVED_STATE:
            return ResponseRedirect('https://sotu.cocoapods.org/removed')

        if self.enforce_attendee_limit and self.has_reached_limit and self.invitation.state == Invitation.INVITED_STATE:
            return ResponseRedirect('https://sotu.cocoapods.org/cap')

        self.perform(self.invitation)
        return super(InvitationView, self).get(*args, **kwargs)


class AcceptView(InvitationView):
    template_name = 'accepted.html'
    expected_states = (Invitation.INVITED_STATE, Invitation.ACCEPTED_STATE)

    def perform(self, invitation):
        if invitation.state != Invitation.ACCEPTED_STATE:
            invitation.accept()
            invitation.save()


class RejectView(InvitationView):
    template_name = 'rejected.html'
    expected_states = (Invitation.INVITED_STATE, Invitation.ACCEPTED_STATE, Invitation.REJECTED_STATE)
    enforce_attendee_limit = False

    def perform(self, invitation):
        if invitation.state != Invitation.REJECTED_STATE:
            invitation.reject()
            invitation.save()


def callback(request):
    code = request.GET.get('code')
    if not code:
        error = request.GET.get('error')
        error_description = request.GET.get('error_description', 'Unknown Error, please try again')
        return JinjaResponse(request, template_names=['error.html'],
                context={'reason': '{} ({})'.format(error_description, error)})

    access_token = retrieve_access_token(code)
    if not access_token:
        return ResponseRedirect('https://sotu.cocoapods.org/')
    user = retrieve_account(access_token)
    email = retrieve_email(access_token)
    username = user['login']

    name = user.get('name', username)
    if name is None or len(name) == 0:
        name = username

    avatar = user.get('avatar_url', None)

    try:
        entrant = Entrant.select().where(Entrant.github_username == username).get()
    except Entrant.DoesNotExist:
        entrant = Entrant.create(github_username=username, name=name, email=email)

    try:
        invitation = entrant.invitation_set.get()
    except Invitation.DoesNotExist:
        invitation = None

    if invitation:
        if invitation.state == Invitation.ACCEPTED_STATE:
            return ResponseRedirect(invitation.accept_url)
        elif invitation.state == Invitation.REJECTED_STATE:
            return ResponseRedirect(invitation.reject_url)
        elif invitation.state == Invitation.INVITED_STATE:
            return ResponseRedirect(invitation.invited_url)

    return EntrantView.as_view(entrant=entrant, avatar=avatar)(request)


def status_view(request):
    status = {
        'entrants': Entrant.select().count(),
        'invited': Invitation.select().where(Invitation.state == Invitation.INVITED_STATE).count(),
        'accepted': Invitation.select().where(Invitation.state == Invitation.ACCEPTED_STATE).count(),
        'rejected': Invitation.select().where(Invitation.state == Invitation.REJECTED_STATE).count(),
    }
    return Response(json.dumps(status), content_type='application/json')
