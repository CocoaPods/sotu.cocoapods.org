import os
import urllib
import requests
import peewee

from rivr import Router, MiddlewareController, DebugMiddleware, Response
from rivr.http import ResponseRedirect
from rivr.wsgi import WSGIHandler
from rivr_jinja import *
from jinja2 import Environment, PackageLoader

from sotu.models import database, Entrant


GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
GITHUB_CALLBACK_URI = 'https://sotu.cocoapods.org/callback'


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

def retrieve_access_token(code):
    parameters = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
    }
    headers = {
        'Accept': 'application/json',
    }
    response = requests.post('https://github.com/login/oauth/access_token?' + urllib.urlencode(parameters), headers=headers)
    return response.json().get('access_token')


def retrieve_account(access_token):
    return requests.get('https://api.github.com/user?' + urllib.urlencode({'access_token': access_token})).json()

def retrieve_email(access_token):
    emails = requests.get('https://api.github.com/user/emails?' + urllib.urlencode({'access_token': access_token})).json()
    primaries = (e for e in emails if e['primary'] is True)
    return primaries.get()['email']


def callback(request):
    code = request.GET['code']
    access_token = retrieve_access_token(code)
    if not access_token:
        return ResponseRedirect('https://sotu.cocoapods.org/')
    user = retrieve_account(access_token)
    email = retrieve_email(access_token)
    username = user['login']
    name = user['name']
    avatar = user['avatar_url']

    try:
        entrant = Entrant.select().where(Entrant.github_username == username).get()
    except Entrant.DoesNotExist:
        entrant = Entrant.create(github_username=username, name=name, email=email)

    return EntrantView.as_view(entrant=entrant, avatar=avatar)(request)


router = Router(
    (r'^$', IndexView.as_view()),
    (r'^callback$', callback)
)


env = Environment(loader=PackageLoader('sotu', 'templates'))
middleware = MiddlewareController.wrap(router,
    DebugMiddleware(),
    database,
    JinjaMiddleware(env),
)
wsgi = WSGIHandler(middleware)
