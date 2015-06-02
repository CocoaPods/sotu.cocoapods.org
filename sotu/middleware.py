from rivr import Router, MiddlewareController, Response
from rivr_jinja import JinjaMiddleware
from jinja2 import Environment, PackageLoader

from sotu.models import database
from sotu.views import IndexView, callback


router = Router(
    (r'^$', IndexView.as_view()),
    (r'^callback$', callback)
)


env = Environment(loader=PackageLoader('sotu', 'templates'))
middleware = MiddlewareController.wrap(router,
    database,
    JinjaMiddleware(env),
)

