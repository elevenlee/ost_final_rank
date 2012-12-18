import jinja2
import os
import urllib
import webapp2
import rankdata

from google.appengine.ext import db
from google.appengine.api import users

jinji2_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
