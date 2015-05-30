from rivr import Response
from rivr.wsgi import WSGIHandler


def view(request):
    return Response('Come back later ;).', content_type='text/plain')


wsgi = WSGIHandler(view)

