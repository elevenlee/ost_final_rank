import jinja2
import os
import urllib
import webapp2
import rankdata
import util

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
add_page_path = 'category/add'
add_action_path = 'category/addaction'
edit_page_path = 'category/edit'
delete_page_path = 'category/delete'
delete_action_path = 'category/deleteaction'
select_page_path = 'category/select'

def get_category(author, name):
    category_key = db.Key.from_path('Category', '{author}/{name}'.format(author=author, name=name))
    return db.get(category_key)

def get_categories(author):
    category_query = rankdata.Category.all().filter("author = ", author)
    return category_query.run()

def delete_categories(author, names=[]):
    for name in names:
        key = db.Key.from_path('Category', '{author}/{name}'.format(author=author, name=name))
        db.delete(key)

def delete_all_categories(author):
    category_query = rankdata.Category.all().filter("author = ", author)
    for category in category_query.run():
        db.delete(category)

class AddCategoryPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('name')
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
            'name': name,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=add_page_path))
        self.response.out.write(template.render(template_values))

class AddCategoryAction(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name')
        if '/' in name:
            self.redirect('/{path}?'.format(path=add_page_path) + urllib.urlencode({'name': name}))
            return

        user = users.get_current_user()
        if get_category(user, name):
            self.redirect('/{path}?'.format(path=add_page_path) + urllib.urlencode({'name': name}))
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
        name = self.request.get('name')
        names = util.parse_string(name) if name else None
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_value = {
            'categories': categories,
            'url': url,
            'user': user,
            'names': names,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=delete_page_path))
        self.response.out.write(template.render(template_value))

class DeleteCategoryAction(webapp2.RequestHandler):
    def post(self):
        names = self.request.get_all('name')
        command = self.request.get('delete')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)

        if 'Delete' in command:
            delete_categories(user, names)
        elif 'Clear' in command:
            delete_all_categories(user)
        self.redirect('/{path}?'.format(path=delete_page_path) + urllib.urlencode({'name': [name for name in names]}))

class SelectCategoryPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_value = {
            'categories': categories,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=select_page_path))
        self.response.out.write(template.render(template_value))

app = webapp2.WSGIApplication([('/{path}'.format(path=add_page_path), AddCategoryPage),
                               ('/{path}'.format(path=add_action_path), AddCategoryAction),
                               ('/{path}'.format(path=edit_page_path), EditCategoryPage),
                               ('/{path}'.format(path=delete_page_path), DeleteCategoryPage),
                               ('/{path}'.format(path=delete_action_path), DeleteCategoryAction),
                               ('/{path}'.format(path=select_page_path), SelectCategoryPage)],
                              debug=True)
