import jinja2
import os
import urllib
import webapp2
import category
import item

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
select_category_page_path = 'export/selectcategory'
select_category_action_path = 'export/selectcategoryaction'
result_page_path = 'export/result'

class SelectCategoryPage(webapp2.RequestHandler):
    def get(self):
        invalid_select = self.request.get('select_category')
        user = users.get_current_user()
        categories = category.get_categories()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)

        template_values = {
            'categories': categories,
            'url': url,
            'user': user,
            'invalid_select': invalid_select,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=select_category_page_path))
        self.response.out.write(template.render(template_values))

class SelectCategoryAction(webapp2.RequestHandler):
    def get(self):
        category_key = self.request.get('category_key')
        if not category_key:
            self.redirect('/{path}?'.format(path=select_category_page_path) +
                          urllib.urlencode({'select_category': 'Nothing'}))
            return

        category_data = category.get_category_by_key(key=category_key)
        items = item.get_items(author=category_data.author, category_name=category_data.name)

        template_values = {
            'category': category_data,
            'items': items,
        }
        template = jinja_environment.get_template('{path}.xml'.format(path=result_page_path))
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/{path}'.format(path=select_category_page_path), SelectCategoryPage),
                               ('/{path}'.format(path=select_category_action_path), SelectCategoryAction)],
                              debug=True)
