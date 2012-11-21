'''
Entry of WEBlog

Created on 2012-10-26

@author: DANG Zhengfa
'''
# load system modules
import webapp2
# from webapp2 import RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from webapp2 import uri_for, Route
from webapp2_extras.routes import RedirectRoute
from webapp2_extras import json
from model import Entry, Link, Comment, Category
import logging

# load modules defined by this app
from utilities import render_template, dump, get_safe_slug
from BaseRequestHandler import BaseRequestHandler


class Admin(BaseRequestHandler):
    '''
    classdocs
    '''

    def get(self):
        t_values = {}
        t_values['entry'] = ""
        return self.response.out.write(render_template("index.html", t_values, "", True))


class PostManager(BaseRequestHandler):
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
                    if not current_post.is_external_page:
                        current_post.category.entrycount += 1
                        current_post.category.put()
                        current_post.is_external_page = True
                        current_post.put()
                        t_values['alert_message'] = "Post %s has been changed to public" % (current_post.title)
                    else:
                        t_values['alert_message'] = "Post %s was public already" % (current_post.title)
                elif operation == "unpublish":
                    if current_post.is_external_page:
                        current_post.category.entrycount -= 1
                        current_post.category.put()
                        current_post.is_external_page = False
                        current_post.put()
                        t_values['alert_message'] = "Post %s has been changed to private" % (current_post.title)
                    else:
                        t_values['alert_message'] = "Post %s was private already" % (current_post.title)
                elif operation == "delete":
                    if current_post.is_external_page:
                        current_post.category.entrycount -= 1
                        current_post.category.put()
                    current_post.delete()
                    t_values['alert_message'] = "Post %s has been changed to deleted" % (current_post.title)

        # show all posts
        posts = Entry.all().filter("entrytype =", 'post')
        t_values['posts'] = posts

        # load all categories
        categories = Category.all().order("name")
        t_values['categories'] = categories

        return self.response.out.write(render_template("posts.html", t_values, "", True))

    def post(self):
        # add new post or edit existed post
        t_values = {}
        current_post_id = self.request.POST["current_post_id"]
        post_title = self.request.POST["blog_title"]
        post_slug = get_safe_slug(self.request.POST["blog_slug"])
        post_content = self.request.POST["blog_content"]
        # find category
        blog_category_id = self.request.POST["blog_category_id"]
        post_category = Category.get_by_id(long(blog_category_id))
        if post_category:
            logging.info("find category %s for id %s" % (post_category.name, blog_category_id))
        else:
            logging.error("category id %s can't be located" % (blog_category_id))

        if current_post_id:
            logging.info("PostManager: post : edit post current_post_id = %s" % (current_post_id))
            # update existed post
            post = Entry.get_by_id(long(current_post_id))
            if post:
                t_values['alert_message'] = "Post %s has been updated!" % (post.title)
                post.title = post_title
                post.slug = post_slug
                post.content = post_content
                post.entrytype = "post"
                # update category count if this post is public
                if post.is_external_page and post.category != post_category:
                    if post.category and (post.category.entrycount > 0):
                        post.category.entrycount -= 1
                        post.category.put()
                    post_category.entrycount += 1
                    post.category.put()
                post.category = post_category
                post.put()
        else:
            logging.info("PostManager: post : new post title %s" % (self.request.POST['blog_title']))
            # create new post
            post = Entry()
            post.title = post_title
            post.slug = post_slug
            post.content = post_content
            post.entrytype = 'post'
            post.category = post_category
            # save as public or private?
            operation = self.request.POST["submit_action"]
            if operation == "save_publish":
                post.is_external_page = True
                # update category count
                post.category.entrycount += 1
                post.category.put()
            else:  # "save" operation
                post.is_external_page = False
            # save the post
            post.put()
            t_values['alert_message'] = "Post %s has been created!" % (post.title)

        # show all posts
        posts = Entry.all().filter("entrytype =", 'post')
        t_values['posts'] = posts
        return self.response.out.write(render_template("posts.html", t_values, "", True))


class PageManager(BaseRequestHandler):
    def get(self, page_id="", operation=""):
        t_values = {}
        logging.info("PageManager get: page_id = %s, operation = %s" % (page_id, operation))

        # find current_post based on page_id
        if page_id:
            current_post = Entry.get_by_id(long(page_id))
            if current_post:
                logging.info("find post %s from post id %s" % (page_id, current_post.title))
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
        posts = Entry.all().filter("entrytype =", 'page')
        t_values['posts'] = posts
        return self.response.out.write(render_template("pages.html", t_values, "", True))

    def post(self):
        t_values = {}
        # add new post or edit existed post
        current_post_id = self.request.POST["current_post_id"]
        if current_post_id:
            logging.info("PageManager: post : current_post_id = %s" % (current_post_id))
            # update existed post
            post = Entry.get_by_id(long(current_post_id))
            if post:
                t_values['alert_message'] = "Post %s has been updated!" % (post.title)
                post.title = self.request.POST["blog_title"]
                post.slug = get_safe_slug(self.request.POST["blog_slug"])
                post.content = self.request.POST["blog_content"]
                post.entrytype = 'page'
                post.put()

        else:
            logging.info("PageManager: post : new post title %s" % (self.request.POST['blog_title']))
            # create new post
            post = Entry()
            post.title = self.request.POST["blog_title"]
            post.slug = get_safe_slug(self.request.POST["blog_slug"])
            post.content = self.request.POST["blog_content"]
            # post.categories = self.request.POST["blog_categories"]
            operation = self.request.POST["submit_action"]
            logging.info("operation = %s" % (operation))
            if operation == "save_publish":
                post.is_external_page = True
            else:  # "save" operation
                post.is_external_page = False
            post.entrytype = 'page'
            post.put()

            t_values['alert_message'] = "Page %s: %s has been created!" % (post.title, post.entrytype)

        # show all posts
        posts = Entry.all().filter("entrytype =", 'page')
        t_values['posts'] = posts
        return self.response.out.write(render_template("pages.html", t_values, "", True))


class CommentManager(BaseRequestHandler):
    def get(self, page_id="", operation=""):
        # find all comments, and list all comments
        t_values = {}
        logging.info("CommentManager get")

        # show all comments
        comments = Comment.all().order("entry")
        t_values['comments'] = comments
        return self.response.out.write(render_template("comments.html", t_values, "", True))

    def post(self):
        # this method is reserved for AJAX call to this object
        # json response
        result = {'message': ""}
        comment_id = self.request.POST.get("comment_id", "")
        operation = self.request.POST.get("operation", "")
        logging.info("CommentManager, post data: comment_id = %s, operation = %s" % (comment_id, operation))
        if comment_id:
            comment = Comment.get_by_id(long(comment_id))
            if comment:
                if operation == "delete":
                    # update entry.commentcount
                    comment.entry.commentcount -= 1
                    comment.entry.put()
                    # delete this comment
                    comment.delete()
                    result['message'] = "comment '%s' has been deleted" % (comment_id)
                else:
                    result['message'] = "unknown operation %s" % (operation)
            else:
                result['message'] = "unknown comment id %s" % (comment_id)
        else:
            result['message'] = "empty comment id"

        json_response = json.encode(result)
        logging.info("json response: %s" % (json_response))

        self.response.content_type = "application/json"
        return self.response.out.write(json_response)


class LinkManager(BaseRequestHandler):
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
            link.target = link_target
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


class CategoryManager(BaseRequestHandler):
    """manage categoriesfor this blog"""
    def get(self):
        t_values = {}
        logging.info("CategoryManager: get")

        # find all categories
        cates = Category.all().order("name")
        t_values["categories"] = cates
        return self.response.out.write(render_template("categories.html", t_values, "", True))

    # add new link, or update existed link
    def post(self):

        result = {'message': ''}

        logging.info(self.request.POST)
        current_cate_id = self.request.POST.get("current_cate_id")
        cate_name = self.request.POST.get("cate_name")
        cate_slug = self.request.POST.get("cate_slug")
        operation = self.request.POST.get("operation")
        logging.info("CategoryManager post: current_cate_id = %s, cate_name = %s, cate_slug = %s, operation = %s" % (current_cate_id, cate_name, cate_slug, operation))

        if current_cate_id:
            # edit existed link
            cate = Category.get_by_id(long(current_cate_id))
            if cate:
                # current_cate_id exists
                if operation == "delete":
                    if cate.entrycount == 0:
                        cate.delete()
                        result['message'] = "category %s has been deleted" % (current_cate_id)
                    else:
                        result['message'] = "category %s can't be delete since it's still being used!" % (current_cate_id)
                else:
                    cate.name = cate_name
                    cate.slug = cate_slug
                    cate.put()
                    result['message'] = "category %s has been updated" % (cate.name)
            else:
                logging.info("category id=%s does not exist!" % (current_cate_id))
        else:
            # create new cate
            cate = Category(name=cate_name, slug=cate_slug)
            cate.put()
            result['message'] = "category %s has been created" % (cate.name)

        # return json result
        self.response.content_type = 'application/json'
        return self.response.out.write(json.encode(result))

# define routers
# see http://webapp-improved.appspot.com/api/webapp2_extras/routes.html
routes = [
          RedirectRoute('/admin/', handler='admin.Admin', name="admin", strict_slash=True),
          Route('/admin/posts', handler='admin.PostManager', name="admin.posts"),
          Route('/admin/posts/<post_id>/<operation>', handler='admin.PostManager', name="admin.posts.operation"),
          Route('/admin/comments', handler='admin.CommentManager', name="admin.comments"),
          Route('/admin/categories', handler='admin.CategoryManager', name="admin.categories"),
          Route('/admin/pages', handler='admin.PageManager', name="admin.pages"),
          Route('/admin/pages/<page_id>/<operation>', handler='admin.PageManager', name="admin.pages.operation"),
          Route('/admin/links', handler='admin.LinkManager', name="admin.links"),
          Route('/admin/links/<link_id>/<operation>', handler='admin.LinkManager', name="admin.links.operation"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
