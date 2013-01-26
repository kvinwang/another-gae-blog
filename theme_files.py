# -*- coding: utf-8 -*-
import os
import stat
import sys
import logging
import wsgiref.handlers
from mimetypes import types_map
from datetime import datetime, timedelta
# from google.appengine.api import memcache
from google.appengine.ext.zipserve import *
sys.path.append('modules')
from utilities import error404
from BaseRequestHandler import BaseRequestHandler

# several global parameters
cwd = os.path.dirname(__file__)
theme_path = os.path.join(cwd, "themes")
file_modifieds = {}
max_age = 600  # expires in 10 minutes




class GetFile(BaseRequestHandler):
    def get(self, theme_name, target_name):
        logging.info("theme_file - GetFile - %s/%s" % (theme_name, target_name))
        request_path = self.request.path[8:]
        server_path = os.path.normpath(os.path.join(cwd, 'themes', request_path))

        try:
            fstat = os.stat(server_path)
        except:
            # check themes exists as a zip file?
            theme_file = os.path.normpath(os.path.join(cwd, 'themes', theme_name))
            if os.path.exists(theme_file + ".zip"):
                # is file exist? find target in zip file
                fstat = os.stat(theme_file + ".zip")
                zipdo = ZipHandler()
                zipdo.initialize(self.request, self.response)
                return zipdo.get(theme_file, target_name)
            else:
                error404(self)
                return

        # request normal file in themes package
        fmtime = datetime.fromtimestamp(fstat[stat.ST_MTIME])
        if self.request.if_modified_since and self.request.if_modified_since.replace(tzinfo=None) >= fmtime:
            # use cached content
            self.response.headers['Date'] = format_date(datetime.utcnow())
            self.response.headers['Last-Modified'] = format_date(fmtime)
            cache_expires(self.response, max_age)
            self.response.set_status(304)
            self.response.clear()
        elif server_path.startswith(theme_path):
            # find minetye for this content
            ext = os.path.splitext(server_path)[1]
            if ext in types_map:
                mime_type = types_map[ext]
            else:
                mime_type = 'application/octet-stream'

            try:
                self.response.headers['Content-Type'] = mime_type
                self.response.headers['Last-Modified'] = format_date(fmtime)
                cache_expires(self.response, max_age)
                self.response.out.write(open(server_path, 'rb').read())
            except Exception, e:
                error404(self)
        else:
            error404(self)


# does not read file contents for templates folders
class NotFound(BaseRequestHandler):
    def get(self):
        error404(self)


def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def cache_expires(response, seconds=0, **kw):
    """
    Set expiration on this request.  This sets the response to
    expire in the given seconds, and any other attributes are used
    for cache_control (e.g., private=True, etc).

    this function is modified from webob.Response
    it will be good if google.appengine.ext.webapp.Response inherits from this class...
    """
    if not seconds:
        # To really expire something, you have to force a
        # bunch of these cache control attributes, and IE may
        # not pay attention to those still so we also set
        # Expires.
        response.headers['Cache-Control'] = 'max-age=0, must-revalidate, no-cache, no-store'
        response.headers['Expires'] = format_date(datetime.utcnow())
        if 'last-modified' not in self.headers:
            self.last_modified = format_date(datetime.utcnow())
        response.headers['Pragma'] = 'no-cache'
    else:
        response.headers['Cache-Control'] = 'max-age=%d' % seconds
        response.headers['Expires'] = format_date(datetime.utcnow() + timedelta(seconds=seconds))


def main():
    application = webapp.WSGIApplication(
            [
                ('/themes/[\\w\\-]+/templates/.*', NotFound),
                ('/themes/(?P<theme_name>[\\w\\-]+)/(?P<target_name>.+)', GetFile),
                ('.*', NotFound),
                ],
            debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
