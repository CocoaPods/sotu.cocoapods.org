import os
import sendgrid


USERNAME = os.environ['SENDGRID_USERNAME']
PASSWORD = os.environ['SENDGRID_PASSWORD']
SENDER = 'CocoaPods <info@cocoapods.org>'

grid = sendgrid.SendGridClient(USERNAME, PASSWORD, raise_errors=True)


def send_email(invitation, subject, body_text):
    message = sendgrid.Mail()
    message.set_from(SENDER)
    message.add_to(invitation.email)
    message.set_subject(subject)
    message.set_text(body_text)
    status, msg = grid.send(message)


def send_invitation(invitation):
    text = u"""Hi {name},

You've been invited to the CocoaPods State of the Union.

You can accept this invitation by following this link:

    {accept_url}

If you cannot make it, please reject this invitation so we can invite another
person.

    {reject_url}

Regards,

The CocoaPods Team
""".format(name=invitation.entrant.name, accept_url=invitation.accept_url, reject_url=invitation.reject_url)
    send_email(invitation, 'CocoaPods State of the Union Invitation', text)


def send_reminder(invitation):
    text = u"""Hi {name},

We've noticed you haven't accepted or rejected your invitation to the CocoaPods
State of the Union yet.

This is a reminder to respond to your invitation soon. We will be giving away
unresponded invitations to other entrants to give them a chance.

You can accept this invitation by following this link:

    {accept_url}

If you cannot make it, please reject this invitation so we can invite another
person.

    {reject_url}

Regards,

The CocoaPods Team
""".format(name=invitation.entrant.name, accept_url=invitation.accept_url, reject_url=invitation.reject_url)
    send_email(invitation, 'CocoaPods State of the Union Invitation', text)
