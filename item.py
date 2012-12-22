import jinja2
import os
import random
import urllib
import webapp2
import rankdata
import category
import comment
import util

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

main_page_path = 'item/index'
add_edit_delete_page_path = 'item/addeditdelete'
add_page_path = 'item/add'
add_action_path = 'item/addaction'
select_item_page_path = 'item/selectedititem'
select_item_action_path  ='item/selectedititemaction'
edit_page_path = 'item/edit'
edit_action_path = 'item/editaction'
delete_page_path = 'item/delete'
delete_action_path = 'item/deleteaction'

def get_ancestor_key(author, category_name):
    """Returns ancestor key of the specified item

    Each item must have a category ancestor. The format of ancestor key
    is 'author/category name'.
    :param author the specified author
    :param category_name the specified category name
    :returns: ancestor key of specified item
    """
    return db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=category_name))

def get_item(author, category_name, item_name):
    """Returns item of specified author, category, and item name

    :param author the specified author
    :param category_name the specified category name
    :param item_name the specified item name
    :returns item of speicfied author, category, and item name
    """
    item_key = db.Key.from_path('Item',
                                '{author}/{category}/{item}'.format(author=author, category=category_name, item=item_name),
                                parent=get_ancestor_key(author, category_name))
    return db.get(item_key)

def get_item_by_key(category_key, item_name):
    """Returns item of specified category key and item name

    Each item must have a category ancestor. The category_key is actually
    the ancestor key of item which format is 'author/category name'.
    :param category_key the specified ancestor key of item
    :param item_name the specified item name
    :returns: item of specified category key and item name
    """
    ancestor_key = db.Key.from_path('Category', category_key)
    item_key = db.Key.from_path('Item',
                                '{category_key}/{item}'.format(category_key=category_key, item=item_name),
                                parent=ancestor_key)
    return db.get(item_key)

def get_items_by_name(keyword):
    """Returns items of specified keyword

    Retrive all items that its name equals keyword. The returned items is
    dictionary type, the key value is the item's ancestor key and the value
    is the item name
    :param keyword the specified keyword
    :returns: items of specified keyword
    """
    item_map = {}
    category_query = rankdata.Category.all()
    for category_data in category_query.run():
        ancestor_key = get_ancestor_key(category_data.author, category_data.name)
        item_query = rankdata.Item.all().ancestor(ancestor_key).filter('name = ', keyword)
        if item_query.count():
            item_map['{author}/{category}'.format(author=category_data.author, category=category_data.name)] = item_query.get().name
    return item_map

def get_items(author, category_name, order='-create_time', count_or_not=False):
    """Returns items of specified author, category, and order. If
       count_or_not set to True, returns the number of items.

    :paramm author the specified author
    :param category_name the specified category name
    :param order the specified order. The default value is ordering by
                 create time field in descending
    :param count_or_not determine return number or actual items. The
                        default value is False which return the actual
                        items
    :returns items of specified author, category, and order. If
             count_or_not set to True, returns the number of items
    """
    ancestor_key = get_ancestor_key(author, category_name)
    item_query = rankdata.Item.all().ancestor(ancestor_key).order(order)
    return item_query.count() if count_or_not else item_query.run()

def get_random_items(category_key, number=2):
    """Returns random items of specified category key

    Each item must have a category ancestor. The category_key is actually
    the ancestor key of item which format is 'author/category name'.
    :param category_key the specified ancestor key
    :param number the number of random items. The default valu is 2
    :returns random items of specified category key
    """
    ancestor_key = db.Key.from_path('Category', category_key)
    item_query = rankdata.Item.all().ancestor(ancestor_key)
    item_list = item_query.fetch(limit=None)
    return [item_list[i] for i in random.sample(range(item_query.count()), number)]

def update_item(author, category_name, new_item_name, old_item_name):
    """Update item of specified author, category name, new item name, and
       old item name

    When update the item name, all comments belonging to the old item as
    well as the vote result would be delete automatically.
    :param author the specified author
    :param category_name the specified category name
    :param new_item_name the specified new item name
    :param old_item_name the specified old item name
    """
    old_item = get_item(author=author, category_name=category_name, item_name=old_item_name)
    comment.delete_all_comments(category_key='{author}/{category}'.format(author=author, category=category_name), item_name=old_item_name)
    db.delete(old_item)

    new_item = rankdata.Item(key_name='{author}/{category}/{item}'.format(author=author, category=category_name, item=new_item_name),
                             parent=get_ancestor_key(author, category_name),
                             name=new_item_name,
                             number_of_win=0, number_of_lose=0, percentage=-1.0)
    new_item.put()

def reserve_all_items(author, new_category_name, old_category_name):
    """Reserve all items as well as comments belonging to when its
       ancestor category name changed

    When update the category name, all items belonging to as well as its
    all comments would be reserved automatically
    :param author the specified author
    :param new_category_name the specified new category name
    :param old_category_name the specified old category name
    """
    old_items = get_items(author=author, category_name=old_category_name)

    for old_item in old_items:
        new_item = rankdata.Item(key_name='{author}/{category}/{item}'.format(author=author, category=new_category_name, item=old_item.name),
                                 parent=get_ancestor_key(author=author, category_name=new_category_name),
                                 name=old_item.name, create_time=old_item.create_time,
                                 number_of_win=old_item.number_of_win, number_of_lose=old_item.number_of_lose,
                                 percentage=old_item.percentage)
        new_item.put()

        old_comments = comment.get_comments(category_key='{author}/{category}'.format(author=author, category=old_category_name), item_name=old_item.name)
        for old_comment in old_comments:
            new_comment = rankdata.Comment(key_name='{author}/{category}/{item}/{commenter}'.format(author=author,
                                                                                                    category=new_category_name,
                                                                                                    item=old_item.name,
                                                                                                    commenter=old_comment.commenter),
                                           parent=comment.get_ancestor_key(category_key='{author}/{category}'.format(author=author, category=new_category_name),
                                                                           item_name=old_item.name),
                                           commenter=old_comment.commenter, content=old_comment.content, submit_time=old_comment.submit_time)
            db.delete(old_comment)
            new_comment.put()

        db.delete(old_item)

def delete_items(author, category_name, item_names=[]):
    """Delete items of specified author, category and item name

    When delete an item, all comments belonging to as well as vote result
    would be delete automatically
    :param author the specified author
    :param category_name the specified category name
    "param item_names the specified item name list
    """
    for item_name in item_names:
        key = db.Key.from_path('Item',
                               '{author}/{category}/{item}'.format(author=author, category=category_name, item=item_name),
                               parent=get_ancestor_key(author, category_name))
        comment.delete_all_comments('{author}/{category}'.format(author=author, category=category_name), db.get(key).name)
        db.delete(key)

def delete_all_items(author, category_name):
    """Delete all items of specified author and category

    When delete an item, all comments belonging to as well as vote result
    would be delete automatically
    :param author the specified author
    :param category_name the specified category name
    """
    ancestor_key = get_ancestor_key(author, category_name)
    item_query = rankdata.Item.all().ancestor(ancestor_key)
    for item in item_query.run():
        comment.delete_all_comments('{author}/{category}'.format(author=author, category=category_name), item.name)
        db.delete(item)

class ItemMainPage(webapp2.RequestHandler):
    """Construct edit item main HTML page

    """
    def get(self):
        """Handle user request

        The edit item main HTML page would list all categories that the
        user have. The user should select one of them to edit items
        """
        invalid_select = self.request.get('select_category')
        user = users.get_current_user()
        categories = category.get_categories(author=user)
        url = users.create_logout_url(self.request.uri)

        template_value = {
            'categories': categories,
            'url': url,
            'user': user,
            'invalid_select': invalid_select,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=main_page_path))
        self.response.out.write(template.render(template_value))

class AddEditDeletePage(webapp2.RequestHandler):
    """Construct add, edit, delete item HTML page

    """
    def get(self):
        """Handle user request

        According to the edit item main page form submition, construct
        add, edit, delete item HTML page
        """
        category_name = self.request.get('category_name')
        if not category_name:
            self.redirect('/{path}?'.format(path=main_page_path) + 
                          urllib.urlencode({'select_category': 'Nothing'}))
            return

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
            invalid_select = self.request.get('select_item')
            template_values = {
                'category_name': category_name,
                'items': items,
                'url': url,
                'user': user,
               'invalid_select': invalid_select,
            }
            template = jinja_environment.get_template('{path}.html'.format(path=select_item_page_path))
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
    """Handle add item form submition

    """
    def post(self):
        """Handle user request

        The item name could not be empty, contains '/' character as well
        as already exist
        """
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

class SelectItemAction(webapp2.RequestHandler):
    """Construct edit item HTML page

    """
    def get(self):
        """Handle user request

        The edit item HTML page would list all items in category
        """
        category_name = self.request.get('category_name')
        item_name = self.request.get('item_name')
        if not item_name:
            self.redirect('/{path}?'.format(path=add_edit_delete_page_path) +
                          urllib.urlencode({'category_name': category_name, 'method': 'Edit', 'select_item': 'Nothing'}))
            return

        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        comments = comment.get_comments(category_key='{author}/{category}'.format(author=user, category=category_name), item_name=item_name)
        invalid_name = self.request.get('invalid_name')

        template_values = {
            'category_name': category_name,
            'item_name': item_name,
            'comments': comments,
            'url': url,
            'user': user,
            'invalid_name': invalid_name,
        }
        template =jinja_environment.get_template('{path}.html'.format(path=edit_page_path))
        self.response.out.write(template.render(template_values))

class EditItemAction(webapp2.RequestHandler):
    """Handle edit item form submition

    """
    def post(self):
        """Handle user request

        The new item name would not be empty, contains '/' character as
        well as already exist. If the user does not change the item name,
        it will do nothing. Otherwise, all comments belonging to would be
        delete automatically
        """
        category_name = self.request.get('category_name')
        old_item_name = self.request.get('item_name').strip()
        new_item_name = self.request.get('new_item_name').strip()
        if not cmp(old_item_name, new_item_name):
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_name': category_name, 'item_name': old_item_name}))
            return

        if new_item_name == '':
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_name': category_name, 'item_name': old_item_name, 'invalid_name': 'empty name'}))
            return
        elif '/' in new_item_name:
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_name': category_name, 'item_name': old_item_name, 'invalid_name': new_item_name}))
            return

        user = users.get_current_user()
        if get_item(author=user, category_name=category_name, item_name=new_item_name):
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_name': category_name, 'item_name': old_item_name, 'invalid_name': new_item_name}))
        else:
            update_item(author=user, category_name=category_name, new_item_name=new_item_name, old_item_name=old_item_name)
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_name': category_name, 'item_name': new_item_name}))

class DeleteItemAction(webapp2.RequestHandler):
    """Handle delete item form submition

    """
    def post(self):
        """Handler user request

        """
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
                               ('/{path}'.format(path=select_item_action_path), SelectItemAction),
                               ('/{path}'.format(path=edit_action_path), EditItemAction),
                               ('/{path}'.format(path=delete_action_path), DeleteItemAction)],
                              debug=True)
