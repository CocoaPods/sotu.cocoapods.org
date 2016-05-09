import os
import logging

from rivr.wsgi import WSGIHandler
from sotu.middleware import middleware


SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')

logger = logging.getLogger('rivr.request')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logger.addHandler(console)


if SLACK_TOKEN and SLACK_CHANNEL:
    from pyslack import SlackHandler
    handler = SlackHandler(SLACK_TOKEN, SLACK_CHANNEL, username='SOTU')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s (%(process)d): %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


if os.environ.get('SENDGRID_USERNAME'):
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('smtp.sendgrid.net',
                               'info@cocoapods.org',
                               ['info@cocoapods.org'],
                               'State of the Union Heroku Exception',
                               credentials=(os.environ['SENDGRID_USERNAME'],
                                            os.environ['SENDGRID_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)
    mail_handler.setFormatter(logging.Formatter("""\
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s
Message:
%(message)s"""))

wsgi = WSGIHandler(middleware)
