from rivr.http import ResponseRedirect
from rivr_jinja import JinjaView, JinjaResponse

from sotu.github import *
from sotu.models import Entrant


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


def callback(request):
    code = request.GET.get('code')
    if not code:
        error = request.GET['error']
        error_description = request.GET['error_description']
        return JinjaResponse(request, template_names=['error.html'],
                context={'reason': error_description})

    access_token = retrieve_access_token(code)
    if not access_token:
        return ResponseRedirect('https://sotu.cocoapods.org/')
    user = retrieve_account(access_token)
    email = retrieve_email(access_token)
    username = user['login']

    name = user.get('name', username)
    if len(name) == 0:
        name = username

    avatar = user.get('avatar_url', None)

    try:
        entrant = Entrant.select().where(Entrant.github_username == username).get()
    except Entrant.DoesNotExist:
        entrant = Entrant.create(github_username=username, name=name, email=email)

    return EntrantView.as_view(entrant=entrant, avatar=avatar)(request)

