import logging

from rivr.wsgi import WSGIHandler
from sotu.middleware import middleware


logger = logging.getLogger('rivr.request')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logger.addHandler(console)

wsgi = WSGIHandler(middleware)

