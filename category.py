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
edit_action_path = 'category/editaction'
edit_category_path = 'category/editcategory'
edit_category_action_path = 'category/editcategoryaction'
delete_page_path = 'category/delete'
delete_action_path = 'category/deleteaction'
item_page_path = 'item/addeditdelete'

def get_category(author, name):
    category_key = db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=name))
    return db.get(category_key)

def get_category_by_key(key):
    category_key = db.Key.from_path('Category', key)
    return db.get(category_key)

def get_categories(author=None, order='-create_time', item_number=0):
    category_query = rankdata.Category.all().filter("author = ", author).order(order) if author else rankdata.Category.all().order(order)
    return [ category for category in category_query.run() if item.get_items(author=category.author, category_name=category.name, count_or_not=True) >= item_number ] if item_number else category_query.run()

def update_category(author, new_name, old_name):
    new_category = rankdata.Category(key_name='{author}/{name}'.format(author=author, name=new_name), author=author, name=new_name)
    new_category.put()
    item.reserve_all_items(author=author, new_category_name=new_name, old_category_name=old_name)
    old_category = get_category(author=author, name=old_name)
    db.delete(old_category)

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
            self.redirect('/{path}?'.format(path=add_page_path) +
                          urllib.urlencode({'invalid_name': 'empty name'}))
            return
        elif '/' in name:
            self.redirect('/{path}?'.format(path=add_page_path) +
                          urllib.urlencode({'invalid_name': name}))
            return

        user = users.get_current_user()
        if get_category(author=user, name=name):
            self.redirect('/{path}?'.format(path=add_page_path) +
                          urllib.urlencode({'invalid_name': name}))
        else:
            category = rankdata.Category(key_name='{author}/{name}'.format(author=user, name=name), author=user, name=name)
            category.put()
            self.redirect('/{path}?'.format(path=item_page_path) +
                          urllib.urlencode({'category_name': name, 'method': 'Add'}))

class EditCategoryPage(webapp2.RequestHandler):
    def get(self):
        invalid_select = self.request.get('select_category')
        user = users.get_current_user()
        categories = get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
            'invalid_select': invalid_select,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=edit_page_path))
        self.response.out.write(template.render(template_values))

class EditCategoryAction(webapp2.RequestHandler):
    def get(self):
        category_name = self.request.get('category_name')
        if not category_name:
            self.redirect('/{path}?'.format(path=edit_page_path) +
                          urllib.urlencode({'select_category': 'Nothing'}))
            return

        invalid_name = self.request.get('invalid_name')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        items = item.get_items(author=user, category_name=category_name)

        template_values = {
            'category_name': category_name,
            'items': items,
            'url': url,
            'user': user,
            'invalid_name': invalid_name,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=edit_category_path))
        self.response.out.write(template.render(template_values))

class EditCategoryNameAction(webapp2.RequestHandler):
    def post(self):
        old_category_name = self.request.get('category_name').strip()
        new_category_name = self.request.get('new_category_name').strip()
        if not cmp(old_category_name, new_category_name):
            self.redirect('/{path}?'.format(path=edit_action_path) +
                          urllib.urlencode({'category_name': old_category_name}))
            return

        if new_category_name == '':
            self.redirect('/{path}?'.format(path=edit_action_path) +
                          urllib.urlencode({'invalid_name': 'empty name', 'category_name': old_category_name}))
            return
        elif '/' in new_category_name:
            self.redirect('/{path}?'.format(path=edit_action_path) +
                          urllib.urlencode({'invalid_name': new_category_name, 'category_name': old_category_name}))
            return

        user = users.get_current_user()
        if get_category(author=user, name=new_category_name):
            self.redirect('/{path}?'.format(path=edit_action_path) +
                          urllib.urlencode({'invalid_name': new_category_name, 'category_name': old_category_name}))
        else:
            update_category(author=user, new_name=new_category_name, old_name=old_category_name)
            self.redirect('/{path}?'.format(path=edit_action_path) +
                          urllib.urlencode({'category_name': new_category_name}))

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
                               ('/{path}'.format(path=edit_action_path), EditCategoryAction),
                               ('/{path}'.format(path=edit_category_action_path), EditCategoryNameAction),
                               ('/{path}'.format(path=delete_page_path), DeleteCategoryPage),
                               ('/{path}'.format(path=delete_action_path), DeleteCategoryAction)],
                              debug=True)
