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
    """Returns category of the specified author, and name

    :param author: the specified category author
    :param name: the specified category name
    :returns: category of the specified author and name
    """
    category_key = db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=name))
    return db.get(category_key)

def get_category_by_key(key):
    """Returns category of specified key

    :param key the specified key
    :returns: category of the specified key
    """
    category_key = db.Key.from_path('Category', key)
    return db.get(category_key)

def get_categories_by_name(keyword):
    """Returns categories of specified keyword

    Retrive all categories that its name equals keyword
    :param keyword the specified keyword
    :returns: categories of specified keyword
    """
    category_query = rankdata.Category.all().filter('name = ', keyword)
    return category_query.fetch(limit=None)

def get_categories(author=None, order='-create_time', item_number=0):
    """Returns categories of specified author, order and the number of
       item in category is equals to or greater than the specified item
       number

    :param author the specified author. The default value is None,
                  if so, the all categories would be returned
    :param order the specified order. The default value is ordering by
                 create time field in descending
    :param item_number the specified item number. The default value is 0
    :returns: categories of specified author, order and the number of
              item in category is euqlas to or greater than the specified
              item number
    """
    category_query = rankdata.Category.all().filter("author = ", author).order(order) if author else rankdata.Category.all().order(order)
    return [ category for category in category_query.run() if item.get_items(author=category.author, category_name=category.name, count_or_not=True) >= item_number ] if item_number else category_query.run()

def update_category(author, new_name, old_name):
    """Update category of specified author, old name, and new name

    When update the category name, all items belonging to as well as
    its all comments would be reserved automatically.
    :param author the specified author
    :param new_name the specified new category name
    :param old_name the specified old category name
    """
    new_category = rankdata.Category(key_name='{author}/{name}'.format(author=author, name=new_name), author=author, name=new_name)
    new_category.put()
    item.reserve_all_items(author=author, new_category_name=new_name, old_category_name=old_name)
    old_category = get_category(author=author, name=old_name)
    db.delete(old_category)

def delete_categories(author, names=[]):
    """Delete categories of specified author and name

    When delete a category, all items belonging to as well as its all
    comments would be delete automatically.
    :param author the specified author
    :param names the specified name list
    """
    for name in names:
        key = db.Key.from_path('Category', '{author}/{category}'.format(author=author, category=name))
        item.delete_all_items(author, db.get(key).name)
        db.delete(key)

def delete_all_categories(author):
    """Delete all categories of specified author

    When delete a category, all items belonging to as well a its all
    comments would be delete automatically
    :param author the specified author
    """
    category_query = rankdata.Category.all().filter("author = ", author)
    for category in category_query.run():
        item.delete_all_items(author, category.name)
        db.delete(category)

class AddCategoryPage(webapp2.RequestHandler):
    """Construct add category HTML page

    """
    def get(self):
        """Handle user request

        The add category HTML page would list all categories that the
        user already have.
        """
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
    """Handle add category form submition

    """
    def post(self):
        """Handle user request

        The category name could not be empty, comtains '/' character as
        well as already exist.
        """
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
    """Construct edit category HTML page

    """
    def get(self):
        """Handle user request

        The edit category HTML page would list all categories that user
        already have.
        """
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
    """Handle edit category form submition and construct edit category
       name HTML page

    """
    def get(self):
        """Handler user request

        The edit category name HTML page would list all items belonging to
        the specified category.
        """
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
    """Handle edit category name form submition

    """
    def post(self):
        """Handler user request

        The new category name would not be empty, contains '/' character as
        well as already exist. If the user does not change the category name,
        it will do nothing. Otherwise, all items belonging to as well as its
        all comments would be reserved automatically.
        """
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
    """Construct delete category HTML page

    """
    def get(self):
        """Handle user request

        The delete category HTML page would list all categories that user
        already have as well as categories that user just deleted
        """
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
    """Handle delete category form submition

    """
    def post(self):
        """Handle user request

        """
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
