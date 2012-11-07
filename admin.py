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
from model import Entry, Link
import logging

# load modules defined by this app
from utilities import render_template, dump


class Admin(RequestHandler):
    '''
    classdocs
    '''

    def get(self):
        t_values = {}
        t_values['entry'] = ""
        return self.response.out.write(render_template("index.html", t_values, "", True))


class PostManager(RequestHandler):
    def get(self, post_id="", operation=""):
        t_values = {}
        logging.info("PostManager get: post_id = %s, operation = %s" % (post_id, operation))

        # find current_post based on post_id
        if post_id:
            current_post = Entry.get_by_id(long(post_id))
            if current_post:
                logging.info("find post %s from post id %s" % (post_id, current_post.title))
                if operation == "edit":
                    t_values['current_post'] = current_post
                elif operation == "publish":
                    current_post.is_external_page = True
                    current_post.put()
                    t_values['alert_message'] = "Post %s has been changed to public" % (current_post.title)
                elif operation == "unpublish":
                    current_post.is_external_page = False
                    current_post.put()
                    t_values['alert_message'] = "Post %s has been changed to private" % (current_post.title)
                elif operation == "delete":
                    current_post.delete()
                    t_values['alert_message'] = "Post %s has been changed to deleted" % (current_post.title)

        # show all posts
        posts = Entry.all()
        t_values['posts'] = posts
        return self.response.out.write(render_template("posts.html", t_values, "", True))

    def post(self):
        t_values = {}
        # add new post or edit existed post
        current_post_id = self.request.POST["current_post_id"]
        if current_post_id:
            # update existed post
            post = Entry.get_by_id(long(current_post_id))
            if post:
                t_values['alert_message'] = "Post %s has been updated!" % (post.title)
                post.title = self.request.POST["blog_title"]
                post.slug = self.request.POST["blog_slug"]
                post.content = self.request.POST["blog_content"]
                post.put()

        else:
            # create new post
            post = Entry()
            post.title = self.request.POST["blog_title"]
            post.slug = self.request.POST["blog_slug"]
            post.content = self.request.POST["blog_content"]
            # post.categories = self.request.POST["blog_categories"]
            operation = self.request.POST["submit_action"]
            if operation == "Save & Publish":
                post.is_external_page = True
            else:
                post.is_external_page = False
            post.put()
            t_values['alert_message'] = "Post %s has been created!" % (post.title)

        # show all posts
        posts = Entry.all()
        t_values['posts'] = posts
        return self.response.out.write(render_template("posts.html", t_values, "", True))


class LinkManager(RequestHandler):
    """manage external links for this blog"""
    def get(self, link_id="", operation=""):
        t_values = {}
        logging.info("LinkManager: link_id = %s, operation = %s" % (link_id, operation))

        # find current_link from link_id
        if link_id:
            current_link = Link.get_by_id(long(link_id))
            if current_link:
                logging.info("found link %s from link_id: %s" % (current_link.title, link_id))
                if operation == "delete":
                    current_link.delete()
                    t_values['alert_message'] = "Link %s has been deleted." % (current_link.title)
                    # t_values['redirect_location'] = uri_for("admin.links")
                    # return self.response.out.write(render_template("alert.html", t_values, "", True))
                elif operation == "edit":
                    # pass current_link to template
                    t_values['current_link'] = current_link

        # find all links
        links = Link.all().order("-date")
        t_values["links"] = links
        return self.response.out.write(render_template("links.html", t_values, "", True))

    # add new link, or update existed link
    def post(self):
        t_values = {}
        current_link_id = self.request.POST['current_link_id']
        link_title = self.request.POST['link_title']
        link_target = self.request.POST['link_target']
        link_sequence = self.request.POST['link_sequence']
        logging.info("LinkManager post: current_link_id = %s, link_title = %s, link_target = %s, link_sequence = %s" % (current_link_id, link_title, 'link_target', 'link_sequence'))

        if current_link_id:
            # edit existed link
            link = Link.get_by_id(long(current_link_id))
            link.title = link_title
            link.target =link_target
            link.sequence = long(link_sequence)
            link.put()
            t_values['alert_message'] = "link %s has been updated" % (link.title)
        else:
            # create new link
            link = Link(title=link_title, target=link_target, sequence=long(link_sequence))
            link.put()
            t_values['alert_message'] = "link %s has been added" % (link.title)

        # find all links
        links = Link.all().order("-date")
        t_values["links"] = links
        return self.response.out.write(render_template("links.html", t_values, "", True))


# define routers
# see http://webapp-improved.appspot.com/api/webapp2_extras/routes.html
routes = [
          RedirectRoute('/admin/', handler='admin.Admin', name="admin", strict_slash=True),
          Route('/admin/posts', handler='admin.PostManager', name="admin.posts"),
          Route('/admin/posts/<post_id>/<operation>', handler='admin.PostManager', name="admin.posts.operation"),
          Route('/admin/links', handler='admin.LinkManager', name="admin.links"),
          Route('/admin/links/<link_id>/<operation>', handler='admin.LinkManager', name="admin.links.operation"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
