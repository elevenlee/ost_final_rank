import jinja2
import os
import urllib
import webapp2
import rankdata
import item
import util

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
add_page_path = 'category/add'
add_action_path = 'category/addaction'
edit_page_path = 'category/edit'
delete_page_path = 'category/delete'
delete_action_path = 'category/deleteaction'

def get_category(author, name):
    category_key = db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=name))
    return db.get(category_key)

def get_categories(author, order='-create_time'):
    category_query = rankdata.Category.all().filter("author = ", author).order(order)
    return category_query.run()

def delete_categories(author, names=[]):
    for name in names:
        key = db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=name))
        item.delete_all_items(author, db.get(key).name)
        db.delete(key)

def delete_all_categories(author):
    category_query = rankdata.Category.all().filter("author = ", author)
    for category in category_query.run():
        item.delete_all_items(author, category.name)
        db.delete(category)

class AddCategoryPage(webapp2.RequestHandler):
    def get(self):
        invalid_name = self.request.get('invalid_name')
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
            'invalid_name': invalid_name,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=add_page_path))
        self.response.out.write(template.render(template_values))

class AddCategoryAction(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('category_name').strip()
        if name == '':
            self.redirect('/{path}?'.format(path=add_page_path) + urllib.urlencode({'invalid_name': 'empty name'}))
            return
        elif '/' in name:
            self.redirect('/{path}?'.format(path=add_page_path) + urllib.urlencode({'invalid_name': name}))
            return

        user = users.get_current_user()
        if get_category(author=user, name=name):
            self.redirect('/{path}?'.format(path=add_page_path) + urllib.urlencode({'invalid_name': name}))
        else:
            category = rankdata.Category(key_name='{author}/{name}'.format(author=user, name=name), author=user, name=name)
            category.put()
            self.redirect('/')

class EditCategoryPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=edit_page_path))
        self.response.out.write(template.render(template_values))

class DeleteCategoryPage(webapp2.RequestHandler):
    def get(self):
        delete_name = self.request.get('delete_name')
        delete_names = util.parse_string(delete_name) if delete_name else None
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_value = {
            'categories': categories,
            'url': url,
            'user': user,
            'delete_names': delete_names,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=delete_page_path))
        self.response.out.write(template.render(template_value))

class DeleteCategoryAction(webapp2.RequestHandler):
    def post(self):
        command = self.request.get('delete')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)

        if 'Delete' in command:
            category_names = self.request.get_all('category_name')
            delete_categories(user, category_names)
        elif 'Clear' in command:
            category_names = [entity.name for entity in get_categories(author=user)]
            delete_all_categories(user)
        self.redirect('/{path}?'.format(path=delete_page_path) + urllib.urlencode({'delete_name': [name for name in category_names]}))

app = webapp2.WSGIApplication([('/{path}'.format(path=add_page_path), AddCategoryPage),
                               ('/{path}'.format(path=add_action_path), AddCategoryAction),
                               ('/{path}'.format(path=edit_page_path), EditCategoryPage),
                               ('/{path}'.format(path=delete_page_path), DeleteCategoryPage),
                               ('/{path}'.format(path=delete_action_path), DeleteCategoryAction)],
                              debug=True)
