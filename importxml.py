import jinja2
import os
import urllib
import xml.dom.minidom
import webapp2
import rankdata
import category
import item

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
import_page_path = 'import/index'
import_action_path = 'import/action'
edit_category_page_path = 'category/editaction'

def update_category(author, category_name, item_names=[]):
    """Update category of specified author, category name. and item name

    If te category name does not exist in the specified author, it would
    add the category and all items in the item name list and belongs to
    that category. Otherwise, delete all items as well as comments belonging
    to that does not exist in the item name list, then add all new items
    in the item name list.
    :param author the specified author
    :param category_name the specified category name
    :param item_names the specified item name list
    """
    if category.get_category(author=author, name=category_name):
        old_items = item.get_items(author=author, category_name=category_name)
        delete_item_names = [old_item.name for old_item in old_items if old_item.name not in item_names]
        item.delete_items(author=author, category_name=category_name, item_names=delete_item_names)
        for item_name in item_names:
            if not item.get_item(author=author, category_name=category_name, item_name=item_name):
                new_item = rankdata.Item(key_name='{author}/{category}/{name}'.format(author=author, category=category_name, name=item_name),
                                         parent=item.get_ancestor_key(author=author, category_name=category_name),
                                         name=item_name, number_of_win=0, number_of_lose=0, percentage=-1.0)
                new_item.put()
    else:
        new_category = rankdata.Category(key_name='{author}/{name}'.format(author=author, name=category_name), author=author, name=category_name)
        new_category.put()
        for item_name in item_names:
            new_item = rankdata.Item(key_name='{author}/{category}/{name}'.format(author=author, category=category_name, name=item_name),
                                     parent=item.get_ancestor_key(author=author, category_name=category_name),
                                     name=item_name, number_of_win=0, number_of_lose=0, percentage=-1.0)
            new_item.put()

class ImportMainPage(webapp2.RequestHandler):
    """Construct import main HTML page

    """
    def get(self):
        """Handle user request

        """
        invalid_select = self.request.get('select_file')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)

        template_values = {
            'url': url,
            'user': user,
            'invalid_select': invalid_select,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=import_page_path))
        self.response.out.write(template.render(template_values))

class ImportAction(webapp2.RequestHandler):
    """Handle import file form submition

    """
    def post(self):
        """Handle user request

        When usr import a XML file, it would update category information.
        """
        file_name = self.request.POST.multi['filename']
        if not file_name:
            self.redirect('/{path}?'.format(path=import_page_path) +
                          urllib.urlencode({'select_file': 'empty file name'}))
            return
        elif not file_name.endswith('.xml'):
            self.redirect('/{path}?'.format(path=import_page_path) +
                          urllib.urlencode({'select_file': 'No XML file'}))
            return

        user = users.get_current_user()
        with open(file_name, 'r') as f:
            contents = f.read()
        doc = xml.dom.minidom.parseString(contents)
        all_name = doc.getElementsByTagName('NAME')
        category_name = all_name[0].firstChild.data
        item_names = [all_name[i].firstChild.data for i in range(1, len(all_name))]
        update_category(author=user, category_name=category_name, item_names=item_names)

        self.redirect('/{path}?'.format(path=edit_category_page_path) +
                      urllib.urlencode({'category_name': category_name}))

app = webapp2.WSGIApplication([('/{path}'.format(path=import_page_path), ImportMainPage),
                               ('/{path}'.format(path=import_action_path), ImportAction)],
                              debug=True)
