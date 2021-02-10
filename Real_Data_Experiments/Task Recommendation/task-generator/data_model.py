from playhouse.postgres_ext import *
import random

"""
Content of the Task is stored as JSON similar to below.  
{
  "text": [
    {
      "content": "",
      "label": ""
    },
    {
      "content": "",
      "label": ""
    }
  ],
  "image" : [
    {
      "label": "",
      "path" : ""
    }
  ],
  "choice" : [
    {
      "label" : "",
      "options" : []
    }
    ],
  "input" : [
    {
      "label" : ""
    }
    ]
}
"""

pg_db = PostgresqlExtDatabase('postgres', user='user', host='localhost', port=5432)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = pg_db


class TaskType(BaseModel):
    task_type_id = IntegerField(primary_key=True)
    task_keywords = ArrayField(CharField)
    requester = CharField(max_length=999)
    task_description = CharField(max_length=999,null=True)
    task_title = CharField(max_length=999)
    #expected_time = DoubleField(db_column='expected_time',null=True)
    expected_pay = DoubleField(db_column='expected_pay')
    duration = IntegerField(db_column='duration')
    creation_date = TimestampField(db_column='creation_date')


class Task(BaseModel):
    id = IntegerField(primary_key=True)
    task_type = ForeignKeyField(TaskType, backref='type')
    content = JSONField()


class Worker(BaseModel):
    worker_id = CharField(max_length=999,primary_key=True)
    keywords = ArrayField(CharField)
    expected_reward = DoubleField()


class TaskFeatures(BaseModel):
    task_id = ForeignKeyField(Task)
    feature = JSONField()


