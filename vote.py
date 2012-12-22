import jinja2
import os
import urllib
import webapp2
import rankdata
import category
import item

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
select_category_page_path = 'vote/selectcategory'
select_category_action_path = 'vote/selectcategoryaction'
vote_item_page_path = 'vote/voteitem'
vote_item_action_path = 'vote/voteitemaction'
result_page_path = 'vote/result'
result_action_path = 'vote/resultaction'

class SelectCategoryPage(webapp2.RequestHandler):
    def get(self):
        invalid_select = self.request.get('select_category')
        user = users.get_current_user()
        categories = category.get_categories(item_number=2)
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
        category_key = self.request.get('category_key')
        method = self.request.get('method')

        if 'Vote' in method:
            item_names = self.request.get_all('item_name')
            win_item_name = self.request.get('win_item_name')
            lose_item_names = [item_name for item_name in item_names if item_name != win_item_name]
            win_item = item.get_item_by_key(category_key=category_key, item_name=win_item_name)
            lose_item = item.get_item_by_key(category_key=category_key, item_name=lose_item_names[0])
            win_item.number_of_win += 1
            win_item.percentage = round(float(win_item.number_of_win) / float(win_item.number_of_win + win_item.number_of_lose) * 100, 3)
            lose_item.number_of_lose += 1
            lose_item.percentage = round(float(lose_item.number_of_win) / float(lose_item.number_of_win + lose_item.number_of_lose) * 100, 3)
            win_item.put()
            lose_item.put()
            self.redirect('/{path}?'.format(path=select_category_action_path) +
                          urllib.urlencode({'category_key': category_key, 'win': win_item_name, 'lose': lose_item_names[0]}))
        elif 'Skip' in method:
            self.redirect('/{path}?'.format(path=select_category_action_path) +
                          urllib.urlencode({'category_key': category_key}))

class ResultPage(webapp2.RequestHandler):
    def get(self):
        category_key = self.request.get('category_key')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)

        category_data = category.get_category_by_key(key=category_key)
        items = item.get_items(author=category_data.author, category_name=category_data.name, order='-percentage')
        template_values = {
            'category': category_data,
            'items': items,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=result_page_path))
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/{path}'.format(path=select_category_page_path), SelectCategoryPage),
                               ('/{path}'.format(path=select_category_action_path), SelectCategoryAction),
                               ('/{path}'.format(path=vote_item_action_path), VoteItemAction),
                               ('/{path}'.format(path=result_action_path), ResultPage)],
                              debug=True)
