from playhouse.postgres_ext import *
import random


pg_db = PostgresqlExtDatabase('postgres', user='user', host='localhost', port=5432)

class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = pg_db

class Song(BaseModel):
  song_id = IntegerField(primary_key=True, db_column="song_id")
  title = CharField(db_column='title')
  artist = CharField(db_column='artist')
  tempo = DoubleField(db_column='tempo')
  period = IntegerField(db_column='period')
  duration = CharField(db_column='duration')
  popularity = IntegerField(db_column='popularity')
  genre = CharField(db_column='genre')
  album = CharField(db_column='album')

class Worker(BaseModel):
    worker_id = CharField(max_length=999,primary_key=True)
    genres = ArrayField(CharField)
    period = IntegerField()
    tempo = DoubleField()



