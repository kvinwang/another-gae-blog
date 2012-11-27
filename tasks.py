'''
Cronned tasks

Created on 2012-10-26

@author: DANG Zhengfa
'''
# load system modules
import webapp2
from webapp2 import RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from webapp2_extras.routes import RedirectRoute
from webapp2 import uri_for, Route
from google.appengine.api.urlfetch import fetch, InvalidURLError
from google.appengine.api import mail
import datetime
import io
from ConfigParser import ConfigParser, MissingSectionHeaderError
import logging
from datetime import datetime
from pytz.gae import pytz

# from webapp2_extras import i18n

# load modules defined by this app


class IndexHandler(RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        content = "<h1>list of tasks</h1>"
        content += "<ul>"
        content += "<li><a href='%s'>%s</a></li>" % (uri_for("tasks.a820l"), "A820L")
        # add your task here
        # content +=
        content += "</ul>"
        return self.response.out.write(content)


class A820LHandler(RequestHandler):
    '''
    classdocs
    '''
    SKY_URL = "http://dmfile.curitel.com/self_binary/sky_binary/real/download.inf"

    def get(self):
        page_content = ""
        try:
            content = fetch(self.SKY_URL).content
            config = ConfigParser()
            config.readfp(io.BytesIO(content))

            # get localize time using pytz
            cst = pytz.timezone("Asia/Shanghai")
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            sfmt = '%Y-%m-%d %Z'
            ltime = datetime.now(cst)
            ltime_str = ltime.strftime(fmt)
            ltime_str_s = ltime.strftime(sfmt)

            # parse content
            if config.has_section("IM-A820L"):
                version = config.get("IM-A820L", "Version")
                if version != "S1231153":
                    title = "A820L Firmware - NEW @ (GAE) %s" % (ltime_str_s)
                    body = "New version available: %s" % (version)
                else:
                    title = "A820L Firmware - OLD @ (GAE) %s" % (ltime_str_s)
                    body = "Still old version: %s" % (version)
            else:
                title = "A820L Firmware - Unknown @ (GAE) %s" % (ltime_str_s)
                body = "Version not available"

            # send email notification
            body += "\nGenerated at %s GMT" % (ltime_str)
            message = mail.EmailMessage()
            message.sender = "dantifer@gmail.com"
            message.subject = title
            message.to = ["zfdang@freewheel.tv", "dantifer@gmail.com"]
            message.body = body
            message.send()

            page_content = "Email sent: title = %s, content = %s" % (title, body)
            logging.info(page_content)

        except InvalidURLError as e:
            # fetch error
            logging.error("A820LHandler urlfetch.fetch exception %s" % (e))
        except MissingSectionHeaderError as e:
            # ConfigParser error
            logging.error("A820LHandler ConfigParser.read exception %s" % (e))

        return self.response.out.write(page_content)

    def post(self):
        pass


##########################################################
# define routers
routes = [
          RedirectRoute('/tasks/', handler='tasks.IndexHandler', name="tasks.index", strict_slash=True),
          Route('/tasks/a820l', handler='tasks.A820LHandler', name="tasks.a820l"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


# main goes here
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
