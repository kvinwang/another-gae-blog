'''
Created on 2012-9-5

@author: DANG Zhengfa
'''

import jinja2, os, logging
from google.appengine.api import memcache
from webapp2_extras import i18n 


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
        templates_path = os.path.join(os.path.dirname(__file__), "templates/admin/")
    else:
        templates_path = os.path.join(os.path.dirname(__file__), "themes/%s/templates/" % (theme_name))
    logging.info("load template %s/%s" % (templates_path, template_file))

    jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path), extensions=['jinja2.ext.i18n'])
    jinja_environment.install_gettext_translations(i18n)
    jinja_environment.filters['datetime'] = format_datetime

    # load and render the page
    template = jinja_environment.get_template(template_file)

    # update template_values if necessary
    blog = {}
    blog['theme_name'] = "basic"
    template_values['blog'] = blog
    return template.render(template_values)


def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))


def get_safe_slug(original_slug=""):
    if original_slug:
        slug = original_slug.strip()
        slug = slug.replace(" ", "-")
        slug = slug.replace("/", "-")
        slug = slug.replace("\\", "-")
        logging.info("slug translation: %s ==> %s" % (original_slug, slug))
        return slug
    return original_slug
