from rivr import serve
from invoke import task, run
from sotu.models import Entrant
from sotu.middleware import middleware


@task
def migrate():
    Entrant.create_table()


@task
def test():
    run('python -m unittest discover')

