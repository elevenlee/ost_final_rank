import jinja2
import os
import urllib
import webapp2
import category
import item

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
search_page_path = 'search/index'
search_action_path = 'search/action'
result_page_path = 'search/result'

class SearchPage(webapp2.RequestHandler):
    """Construct search HTMl page

    """
    def get(self):
        """Handle user request

        """
        invalid_name = self.request.get('invalid_name')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)

        template_values = {
            'url': url,
            'user': user,
            'invalid_name': invalid_name,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=search_page_path))
        self.response.out.write(template.render(template_values))

class SearchAction(webapp2.RequestHandler):
    """Handle search form submition and construct search result HTMl page

    """
    def get(self):
        """Handle user request

        The search result is divided into two parts: category result and item
        result. In the category result part, user could select a category to
        vote. And in the item result part, user could select a item to submit
        a comment.
        """
        keyword = self.request.get('keyword').strip()
        if keyword == '':
            self.redirect('/{path}?'.format(path=search_page_path) +
                          urllib.urlencode({'invalid_name': 'empty keyword'}))
            return

        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)
        categories = category.get_categories_by_name(keyword=keyword)
        item_map = item.get_items_by_name(keyword=keyword)

        template_values = {
            'categories': categories,
            'item_map': item_map,
            'keyword': keyword,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=result_page_path))
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/{path}'.format(path=search_page_path), SearchPage),
                               ('/{path}'.format(path=search_action_path), SearchAction)],
                              debug=True)
