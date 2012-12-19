import jinja2
import os
import urllib
import webapp2
import rankdata
import category
import item

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
select_category_page_path = 'vote/selectcategory'

class SelectCategoryPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        categories = category.get_categories(item_number=2)
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=select_category_page_path))
        self.response.out.write(template.render(template_values))

class VoteItemPage(webapp2.Requesthandler):
    def get(self):
        pass

app = webapp2.WSGIApplication([('/{path}'.format(path=select_category_page_path), SelectCategoryPage)],
                              debug=True)
