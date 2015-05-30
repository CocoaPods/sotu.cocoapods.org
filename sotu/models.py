import peewee
from rivr_peewee import Database


database = Database()


class Entrant(database.Model):
    github_username = peewee.CharField(unique=True)
    name = peewee.CharField()
    email = peewee.CharField(unique=True)

