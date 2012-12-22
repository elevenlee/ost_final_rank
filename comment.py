import jinja2
import os
import urllib
import webapp2
import rankdata
import category
import item

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
select_category_page_path = 'comment/selectcategory'
select_category_action_path = 'comment/selectcategoryaction'
select_item_page_path = 'comment/selectitem'
select_item_action_path = 'comment/selectitemaction'
make_comment_page_path = 'comment/makecomment'
make_comment_action_path = 'comment/makecommentaction'

def get_ancestor_key(category_key, item_name):
    cate_key = db.Key.from_path('Category', category_key)
    return db.Key.from_path('Item',
                            '{category_key}/{item}'.format(category_key=category_key, item=item_name),
                            parent=cate_key)

def get_comment(category_key, item_name, commenter):
    comment_key = db.Key.from_path('Comment',
                                   '{category_key}/{item}/{commenter}'.format(category_key=category_key, item=item_name, commenter=commenter),
                                   parent=get_ancestor_key(category_key, item_name))
    return db.get(comment_key)

def get_comments(category_key, item_name, order='-submit_time'):
    ancestor_key = get_ancestor_key(category_key, item_name)
    comment_query = rankdata.Comment.all().ancestor(ancestor_key).order(order)
    return comment_query.run()

def delete_all_comments(category_key, item_name):
    ancestor_key = get_ancestor_key(category_key, item_name)
    comment_query = rankdata.Comment.all().ancestor(ancestor_key)
    for comment in comment_query.run():
        db.delete(comment)

class SelectCategoryPage(webapp2.RequestHandler):
    def get(self):
        invalid_select = self.request.get('select_category')
        user = users.get_current_user()
        categories = category.get_categories(item_number=1)
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

        invalid_select = self.request.get('select_item')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri) if user else users.create_login_url(self.request.uri)
        category_data = category.get_category_by_key(key=category_key)
        items = item.get_items(author=category_data.author, category_name=category_data.name)

        template_values = {
            'category': category_data,
            'items': items,
            'url': url,
            'user': user,
            'invalid_select': invalid_select,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=select_item_page_path))
        self.response.out.write(template.render(template_values))

class SelectItemAction(webapp2.RequestHandler):
    def get(self):
        category_key = self.request.get('category_key')
        item_name = self.request.get('item_name')
        if not item_name:
            self.redirect('/{path}?'.format(path=select_category_action_path) +
                          urllib.urlencode({'category_key': category_key, 'select_item': 'Nothing'}))
            return

        invalid_comment = self.request.get('re_comment')
        invalid_content = self.request.get('invalid_content')
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        category_data = category.get_category_by_key(key=category_key)
        comment_item = item.get_item_by_key(category_key=category_key,
                                            item_name=item_name)
        comments = get_comments(category_key=category_key, item_name=item_name)

        template_values = {
            'category': category_data,
            'item': comment_item,
            'comments': comments,
            'url': url,
            'user': user,
            'invalid_comment': invalid_comment,
            'invalid_content': invalid_content,
        }
        template = jinja_environment.get_template('{path}.html'.format(path=make_comment_page_path))
        self.response.out.write(template.render(template_values))

class MakeCommentAction(webapp2.RequestHandler):
    def post(self):
        category_key = self.request.get('category_key')
        item_name = self.request.get('item_name')
        content = self.request.get('content').strip()
        if content == '':
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_key': category_key, 'item_name': item_name, 'invalid_content': 'empty content'}))
            return
        elif len(content) < 10:
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_key': category_key, 'item_name': item_name, 'invalid_content': content}))
            return

        user = users.get_current_user()
        if get_comment(category_key=category_key, item_name=item_name, commenter=user):
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_key': category_key, 'item_name': item_name, 're_comment': 'Replicate'}))
        else:
            comment = rankdata.Comment(key_name='{category_key}/{item}/{commenter}'.format(category_key=category_key, item=item_name, commenter=user),
                                       parent=get_ancestor_key(category_key=category_key, item_name=item_name),
                                       commenter=user, content=content)
            comment.put()
            self.redirect('/{path}?'.format(path=select_item_action_path) +
                          urllib.urlencode({'category_key': category_key, 'item_name': item_name}))

app = webapp2.WSGIApplication([('/{path}'.format(path=select_category_page_path), SelectCategoryPage),
                               ('/{path}'.format(path=select_category_action_path), SelectCategoryAction),
                               ('/{path}'.format(path=select_item_action_path), SelectItemAction),
                               ('/{path}'.format(path=make_comment_action_path), MakeCommentAction)],
                              debug=True)
