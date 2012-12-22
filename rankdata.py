import datetime

from google.appengine.ext import db
from google.appengine.api import users

class Category(db.Model):
    """Store category information

    The category information includes four fields: author, name,
    create time, and last modified time. The author as well as name
    fields are required.

    When store a new category information, the author field would be
    assigned to the current user automatically. Also, the create time
    field would be assigned to the current time automatically only the
    new category add to the datastore other than updating. In a dissimilar
    way, the last modified time field would be assigned to the current
    time automatically at every updating.
    """
    author = db.UserProperty(required=True, auto_current_user_add=True)
    name = db.StringProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    last_modified_time = db.DateTimeProperty(auto_now=True)

class Item(db.Model):
    """Store item information

    The item information includes six fields: name, create time, last
    modified time, number of win, number of lose, and percentage. The
    name, number of win, number of lose, as well as percentage fields
    are required.

    Each item must have a parent indicated the category it belonged to.
    When add a new item information, the create time field would be
    assigned to the current time automatically. The last modified time
    field would be assigned to the current time at every updating.
    """
    name = db.StringProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    last_modified_time = db.DateTimeProperty(auto_now=True)
    number_of_win = db.IntegerProperty(required=True)
    number_of_lose = db.IntegerProperty(required=True)
    percentage = db.FloatProperty(required=True)

class Comment(db.Model):
    """Store comment information

    The comment information includes three fields, commenter, content,
    and submit time. The name as well as content fields are required.

    Each comment must have a parent indicated the item it belonged to.
    When add a new comment information, the commentor would be assigned
    to the current user automatically. In a not dissimilar way, the
    submit time field would be assigned to the current time automatically.
    The comment information is immutable. In other words, once comment
    add to the datastore, it could not be changed ever.
    """
    commenter = db.UserProperty(required=True, auto_current_user_add=True)
    content = db.StringProperty(required=True, multiline=True)
    submit_time = db.DateTimeProperty(auto_now_add=True)

