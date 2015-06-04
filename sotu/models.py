import string
import random
import peewee
from rivr_peewee import Database


database = Database()


def generate_random_string(length=32):
    characters = string.lowercase + string.uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))


class Entrant(database.Model):
    github_username = peewee.CharField(unique=True)
    name = peewee.CharField()
    email = peewee.CharField(unique=True)

    def invite(self):
        invitation = Invitation.create(entrant=self, code=generate_random_string())
        return invitation


class Invitation(database.Model):
    INVITED_STATE = 'invited'  # The user has been invited and has not yet responded
    ACCEPTED_STATE = 'accepted'  # The user accepted the invitation
    REJECTED_STATE = 'rejected'  # The user has rejected the invitation
    ATTENDED_STATE = 'attended'  # The user has checked-in at the event

    STATES = (
        (INVITED_STATE, 'Invited',),
        (ACCEPTED_STATE, 'Accepted',),
        (REJECTED_STATE, 'Rejected',),
        (ATTENDED_STATE, 'Attended',),
    )

    code = peewee.CharField(unique=True)
    entrant = peewee.ForeignKeyField(Entrant, unique=True)
    state = peewee.CharField(choices=STATES, default=INVITED_STATE)

    @property
    def email(self):
        return '{} <{}>'.format(self.entrant.name, self.entrant.email)

    @property
    def reject_url(self):
        return 'https://sotu.cocoapods.org/invitation/{}/reject'.format(self.code)

    @property
    def accept_url(self):
        return 'https://sotu.cocoapods.org/invitation/{}/accept'.format(self.code)

    def accept(self):
        self.state = self.ACCEPTED_STATE

    def reject(self):
        self.state = self.REJECTED_STATE

