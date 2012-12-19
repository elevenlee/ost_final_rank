import jinja2
import os
import urllib
import webapp2
import rankdata
import category

from google.appengine.ext import db
from google.appengine.api import users

jinja2_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

main_page_path = 'item/index'
add_page_path = 'item/add'
add_action_path = 'item/addaction'
edit_page_path = 'item/edit'
delete_page_path = 'item/delete'
delete_action_path = 'item/deleteaction'

class ItemMainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        categories = category.get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_value = {
            'categories': categories,
            'url': url,
            'user': user,
        }
        template = jinja2_environment.get_template('{path}.html'.format(path=main_page_path))
        self.response.out.write(template.render(template_value))

app = webapp2.WSGIApplication([('/{path}'.format(path=main_page_path), ItemMainPage)],
                              debug=True)
