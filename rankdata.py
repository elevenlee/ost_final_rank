import datetime

from google.appengine.ext import db
from google.appengine.api import users

class Category(db.Model):
    author = db.UserProperty(required=True, auto_current_user_add=True)
    name = db.StringProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    last_modified_time = db.DateTimeProperty(auto_now=True)

class Item(db.Model):
    name = db.StringProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    last_modified_time = db.DateTimerProperty(auto_now=True)
    number_of_win = db.IntegerProperty(required=True)
    number_of_lose = db.IntegerProperty(required=True)
    percentage = db.FloatProperty(required=True)

class Comment(db.Model):
    author = db.UserProperty(required=True, auto_current_user_add=True)
    content = db.StringProperty(required=True, multiline=True)
    make_time = db.DateTimeProperty(auto_now_add=True)
