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
from model import Entry, Category, Link, Comment
from utilities import render_template, dump


class IndexHandler(RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        t_values = {}

        # find all entries by order
        entries = Entry.all().filter("is_external_page =", True).order("-date")
        for entry in entries:
            logging.info("entry title: %s, is_external_page = %s" % (entry.title, entry.is_external_page))
        t_values['entries'] = entries

        # find all links
        links = Link.all().order("date")
        t_values['links'] = links

        # find all categories
        categories = Category.all()
        t_values['categories'] = categories

        # show index page
        return self.response.out.write(render_template("index.html", t_values, "basic", False))

    def post(self):
        pass


class PostHandler(RequestHandler):
    '''
    classdocs
    '''
    def get(self, post_slug=""):
        if post_slug:
            t_values = {}

            posts = Entry.all().filter("slug =", post_slug)
            if posts.count() == 1:
                logging.warning("find one post with slug=%s" % (post_slug))
                posts = posts.fetch(limit=1)
                post = posts[0]
                t_values['post'] = post
                dump(post)

                # find all comments
                comments = Comment.all().filter("entry =", post)
                t_values['comments'] = comments
            else:
                logging.warning("%d entries share the same slug %s" % (entries.count(), post_slug))

            links = Link.all().order("date")
            t_values['links'] = links

            categories = Category.all()
            t_values['categories'] = categories
            return self.response.out.write(render_template("post.html", t_values, "basic", False))
        else:
            self.redirect(uri_for("weblog.index"))

    def post(self, post_slug=""):
        if post_slug:
            t_values = {}

            post_id = self.request.POST['post_id']
            post = Entry.get_by_id(long(post_id))
            if post:
                # ok, we find the post, try to add comment to this post
                logging.warning("find one post with post_id %s" % (post_id))

                t_values['post'] = post
                dump(post)

                # create comment for this post
                comm_author = self.request.POST['author']
                comm_email = self.request.POST['email']
                comm_weburl = self.request.POST['weburl']
                comm_content = self.request.POST['comment']
                comm = Comment(entry=post, author=comm_author, email=comm_email, weburl=comm_weburl, content=comm_content)
                comm.put()

                # find all comments
                comments = Comment.all().filter("entry=", post)
                logging.info("PostHandler, post, find %d comments" % (comments.count()))
                if post_id:
                    # only update commentcount when new comment is added
                    post.commentcount = comments.count()
                    post.put()
                t_values['comments'] = comments
            else:
                logging.warning("post_id %s does not exist" % (post_id))


            links = Link.all().order("date")
            t_values['links'] = links

            categories = Category.all()
            t_values['categories'] = categories
            return self.response.out.write(render_template("post.html", t_values, "basic", False))
        else:
            self.redirect(uri_for("weblog.index"))


class PageHandler(RequestHandler):
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
          Route('/', handler='weblog.IndexHandler', name="weblog.index"),
          Route('/page/<page_slug>', handler='weblog.PageHandler', name="weblog.page"),
          Route('/post/<post_slug>', handler='weblog.PostHandler', name="weblog.post"),
          Route('/init', handler='weblog.InitBlog', name="init"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


# main goes here
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
