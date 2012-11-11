'''
Created on 2012-9-5

@author: DANG Zhengfa
'''

import jinja2
import os
import logging
# from google.appengine.api import memcache
from webapp2_extras import i18n
from langs import getLangsList


# 404 method
def error404(handler):
    # show 404 page
    logging.debug("theme_file - error404 - %s" % (handler.request.path))
    handler.response.set_status(404)
    return handler.response.out.write(render_template("404.html", {}, "", True))


# jinja2 filters
def format_datetime(value, format='medium'):
    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "%H:%M %Y-%m-%d"
    return value.strftime(format)


# template loader
def render_template(template_file, template_values={}, theme_name="basic", admin=False):
    # find right path for templates, based on theme / admin
    if admin:
        templates_path = os.path.join(os.path.dirname(__file__), "templates/admin")
    else:
        templates_path = os.path.join(os.path.dirname(__file__), "themes/%s/templates" % (theme_name))
    logging.info("render_template: load file %s/%s" % (templates_path, template_file))
    # logging.info("render_template: jinja2.file = %s" % (jinja2.__file__))

    jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path), extensions=['jinja2.ext.i18n'])
    jinja_environment.install_gettext_translations(i18n)
    jinja_environment.filters['datetime'] = format_datetime

    # load and render the page
    template = jinja_environment.get_template(template_file)

    if not admin:
        # set lang list for all nomal pages
        # update template_values if necessary
        template_values['langs'] = getLangsList()

    return template.render(template_values)


def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))


# blog post slug will be converted into URL-friendly format
def get_safe_slug(original_slug=""):
    if original_slug:
        slug = original_slug.strip()
        slug = slug.replace(" ", "-")
        slug = slug.replace("/", "-")
        slug = slug.replace("\\", "-")
        logging.info("slug translation: %s ==> %s" % (original_slug, slug))
        return slug
    return original_slug

