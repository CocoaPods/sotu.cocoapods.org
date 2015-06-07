import os
from tempfile import NamedTemporaryFile
import peewee
from rivr import serve
from invoke import task, run
from sotu.models import Entrant, Invitation
from sotu.middleware import middleware
from sotu.email import send_invitation, send_reminder, send_remaining_invite


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
def status():
    entrants = Entrant.select().count()
    invited = Invitation.select().where(Invitation.state == Invitation.INVITED_STATE).count()
    accepted = Invitation.select().where(Invitation.state == Invitation.ACCEPTED_STATE).count()
    rejected = Invitation.select().where(Invitation.state == Invitation.REJECTED_STATE).count()
    print('Entrants: {}\n---'.format(entrants))
    print('Invited: {}'.format(invited))
    print('Accepted: {}'.format(accepted))
    print('Rejected: {}'.format(rejected))


@task
def invite(username, force=False):
    try:
        entrant = Entrant.select().where(Entrant.github_username == username).get()
    except Entrant.DoesNotExist:
        print('Username {} does not exist.'.format(username))
        return

    if entrant.invitation_set.exists() and not force:
        print('{} already has an invitation.'.format(username))
        return

    if force:
        invitation = entrant.invitation_set.get()
    else:
        invitation = entrant.invite()

    send_invitation(invitation)


@task
def lottery(amount):
    amount = int(amount)
    entrants = Entrant.select().order_by(peewee.fn.Random()).join(Invitation, JOIN.LEFT_OUTER).group_by(Entrant).having(fn.COUNT(Invitation.id) == 0).limit(amount)
    print('Inviting {} entrants.'.format(len(entrants)))

    for entrant in entrants:
        print(entrant.github_username)
        invitation = entrant.invite()
        send_invitation(invitation)


@task
def remind():
    """
    Sends out a reminder to all of the outstanding invitees who have not
    yet accepted or rejected.
    """

    invitations = Invitation.select().where(Invitation.state == Invitation.INVITED_STATE)

    for invitation in invitations:
        send_reminder(invitation)


@task
def invite_remaining():
    entrants = Entrant.select().order_by(peewee.fn.Random())
    entrants = filter(lambda e: e.invitation_set.count() == 0, entrants)

    for entrant in entrants:
        print(entrant.github_username)
        invitation = entrant.invite()
        send_remaining_invite(invitation)
