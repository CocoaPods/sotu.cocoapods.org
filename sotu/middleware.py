from rivr import Router, MiddlewareController, Response
from rivr.views.static import StaticView
from rivr_jinja import JinjaMiddleware, JinjaView
from jinja2 import Environment, PackageLoader

from sotu.models import database
from sotu.views import IndexView, InvitationView, AcceptView, RejectView, callback


router = Router(
    (r'^$', IndexView.as_view()),
    (r'^callback$', callback),
    (r'^invitation/(?P<code>[\w\d]+)/accept$', AcceptView.as_view()),
    (r'^invitation/(?P<code>[\w\d]+)/reject$', RejectView.as_view()),
    (r'^invitation/(?P<code>[\w\d]+)$', InvitationView.as_view()),
    (r'^removed$', JinjaView.as_view(template_name='removed.html')),
    (r'^(?P<path>.*)$', StaticView.as_view(document_root='sotu/static')),
)


env = Environment(loader=PackageLoader('sotu', 'templates'))
middleware = MiddlewareController.wrap(router,
    database,
    JinjaMiddleware(env),
)

