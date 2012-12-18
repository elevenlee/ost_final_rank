import jinja2
import os
import webapp2

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            signflag = True
        else:
            url = users.create_login_url(self.request.uri)
            signflag = False

        template_values = {
            'signflag': signflag,
            'url': url,
            'user': user,
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
