from sotu.models import Entrant
from invoke import task


@task
def migrate():
    Entrant.create_table()

