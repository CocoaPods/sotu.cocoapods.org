from rivr.wsgi import WSGIHandler
from sotu.middleware import middleware

wsgi = WSGIHandler(middleware)

