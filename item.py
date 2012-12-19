import jinja2
import os
import urllib
import webapp2
import rankdata
import category
import util

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

main_page_path = 'item/index'
add_edit_delete_page_path = 'item/addeditdelete'
add_page_path = 'item/add'
add_action_path = 'item/addaction'
edit_page_path = 'item/edit'
delete_page_path = 'item/delete'
delete_action_path = 'item/deleteaction'

def get_ancestor_key(author, category_name):
    return db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=category_name))

def get_item(author, category_name, item_name):
    item_key = db.Key.from_path('Item',
                                '{author}/{category}/{item}'.format(author=author, category=category_name, item=item_name),
                                parent=get_ancestor_key(author, category_name))
    return db.get(item_key)

def get_items(author, category_name, order='-create_time'):
    ancestor_key = get_ancestor_key(author, category_name)
    item_query = rankdata.Item.all().ancestor(ancestor_key).order(order)
    return item_query.run()

def delete_items(author, category_name, item_names=[]):
    for item_name in item_names:
        key = db.Key.from_path('Item',
                               '{author}/{category}/{item}'.format(author=author, category=category_name, item=item_name),
                               parent=get_ancestor_key(author, category_name))
        db.delete(key)

def delete_all_items(author, category_name):
    ancestor_key = get_ancestor_key(author, category_name)
    item_query = rankdata.Item.all().ancestor(ancestor_key)
    for item in item_query.run():
        db.delete(item)

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
        template = jinja_environment.get_template('{path}.html'.format(path=main_page_path))
        self.response.out.write(template.render(template_value))

class AddEditDeletePage(webapp2.RequestHandler):
    def get(self):
        category_name = self.request.get('category_name')
        method = self.request.get('method')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        items = get_items(author=user, category_name=category_name)

        if 'Add' in method:
            invalid_name = self.request.get('invalid_name')
            template_values = {
                'category_name': category_name,
                'items': items,
                'url': url,
                'user': user,
                'invalid_name': invalid_name,
            }
            template = jinja_environment.get_template('{path}.html'.format(path=add_page_path))
        elif 'Edit' in method:
            pass
        elif 'Delete' in method:
            delete_name = self.request.get('delete_name')
            delete_names = util.parse_string(delete_name) if delete_name else None
            template_values = {
                'category_name': category_name,
                'items': items,
                'url': url,
                'user': user,
                'delete_names': delete_names,
            }
            template = jinja_environment.get_template('{path}.html'.format(path=delete_page_path))
        self.response.out.write(template.render(template_values))

class AddItemAction(webapp2.RequestHandler):
    def post(self):
        category_name = self.request.get('category_name')
        item_name = self.request.get('item_name').strip()
        if item_name == '':
            self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                          urllib.urlencode({'invalid_name': 'empty name', 'category_name': category_name, 'method': 'Add'}))
            return
        elif '/' in item_name:
            self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                          urllib.urlencode({'invalid_name': item_name, 'category_name': category_name, 'method': 'Add'}))
            return

        user = users.get_current_user()
        if get_item(author=user, category_name=category_name, item_name=item_name):
            self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                          urllib.urlencode({'invalid_name': item_name, 'category_name': category_name, 'method': 'Add'}))
        else:
            item = rankdata.Item(key_name='{author}/{category}/{item}'.format(author=user, category=category_name, item=item_name),
                                 parent=get_ancestor_key(author=user, category_name=category_name),
                                 name=item_name, number_of_win=0, number_of_lose=0, percentage=-1.0)
            item.put()
            self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                          urllib.urlencode({'category_name': category_name, 'method': 'Add'}))

class DeleteItemAction(webapp2.RequestHandler):
    def post(self):
        category_name = self.request.get('category_name')
        command = self.request.get('delete')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)

        if 'Delete' in command:
            item_names = self.request.get_all('item_name')
            delete_items(author=user, category_name=category_name, item_names=item_names)
        elif 'Clear' in command:
            item_names = [entity.name for entity in get_items(author=user, category_name=category_name)]
            delete_all_items(author=user, category_name=category_name)
        self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                      urllib.urlencode({'delete_name': [name for name in item_names], 'category_name': category_name, 'method': 'Delete'}))


app = webapp2.WSGIApplication([('/{path}'.format(path=main_page_path), ItemMainPage),
                               ('/{path}'.format(path=add_edit_delete_page_path), AddEditDeletePage),
                               ('/{path}'.format(path=add_action_path), AddItemAction),
                               ('/{path}'.format(path=delete_action_path), DeleteItemAction)],
                              debug=True)
