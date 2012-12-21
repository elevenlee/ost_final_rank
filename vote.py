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
select_category_action_path = 'vote/selectcategoryaction'
vote_item_page_path = 'vote/voteitem'

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

class SelectCategoryAction(webapp2.RequestHandler):
    def get(self):
        category_key = self.request.get('category_key')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)

        win_item_name = self.request.get('win')
        lose_item_name = self.request.get('lose')
        category_data = category.get_category_by_key(key=category_key)
        vote_items = item.get_random_items(category_key=category_key)
        win_item = item.get_item_by_key(category_key=category_key, item_name=win_item_name) if win_item_name else None
        lose_item = item.get_item_by_key(category_key=category_key, item_name=lose_item_name) if lose_item_name else None

        template_values = {
            'category': category_data,
            'items': vote_items,
            'url': url,
            'user': user,
            'win': win_item,
            'lose': lose_item,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=vote_item_page_path))
        self.response.out.write(template.render(template_values))

class VoteItemAction(webapp2.RequestHandler):
    def post(self):
        pass

app = webapp2.WSGIApplication([('/{path}'.format(path=select_category_page_path), SelectCategoryPage),
                               ('/{path}'.format(path=select_category_action_path), SelectCategoryAction)],
                              debug=True)
