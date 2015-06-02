import os
import urllib
import requests


GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
GITHUB_CALLBACK_URI = 'https://sotu.cocoapods.org/callback'


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
    primary = next(e for e in emails if e['primary'] is True)
    return primary['email']

