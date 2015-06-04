import os
from tempfile import NamedTemporaryFile
from rivr import serve
from invoke import task, run
from sotu.models import Entrant, Invitation
from sotu.middleware import middleware


@task
def migrate():
    Entrant.create_table()
    Invitation.create_table()


@task
def test():
    with NamedTemporaryFile() as fp:
        os.environ['DATABASE_URL'] = 'sqlite:///' + fp.name
        os.environ['GITHUB_CLIENT_ID'] = 'test_id'
        os.environ['GITHUB_CLIENT_SECRET'] = 'test_secret'
        os.environ['GITHUB_BASE_URI'] = 'http://localhost:5959'
        os.environ['GITHUB_API_BASE_URI'] = 'http://localhost:5959'
        run('invoke migrate')
        run('python -m unittest discover')


@task
def invite(username):
    try:
        entrant = Entrant.select().where(Entrant.github_username == username).get()
    except Entrant.DoesNotExist:
        print('Username {} does not exist.'.format(username))
        return

    if entrant.invitation_set.exists():
        print('{} already has an invitation.'.format(username))

    entrant.invite()

