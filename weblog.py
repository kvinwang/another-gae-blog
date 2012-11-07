'''
Entry of WEBlog

Created on 2012-10-26

@author: DANG Zhengfa
'''
# load system modules
import webapp2
from webapp2 import RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from webapp2 import uri_for, Route
from webapp2_extras.routes import RedirectRoute
import logging

# load modules defined by this app
from model import Entry, Category, Link
from utilities import render_template


class WEBlog(RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        t_values = {}

        entries = Entry.all().filter("is_external_page =", True).order("-date")
        for entry in entries:
            logging.info("entry title: %s, is_external_page = %s" % (entry.title, entry.is_external_page))
        t_values['entries'] = entries

        links = Link.all().order("date")
        t_values['links'] = links

        categories = Category.all()
        t_values['categories'] = categories
        return self.response.out.write(render_template("index.html", t_values, "basic", False))

    def post(self):
        pass


class InitBlog(RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        link = Link(title="linkx1", target="http://baidu.com", sequence=9)
        link.put()
        

        link = Link(title="linkx2", target="http://baidu.com", sequence=9)
        link.put()

        link = Link(title="linkx3", target="http://baidu.com", sequence=9)
        link.put()
        return self.response.out.write(render_template("index.html", {}, "basic", False))

##########################################################
# define routers
routes = [
          Route('/', handler='weblog.WEBlog', name="blog"),
          Route('/init', handler='weblog.InitBlog', name="init"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


# main goes here
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


