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
from google.appengine.api.urlfetch import fetch, InvalidURLError
from google.appengine.api import mail
import datetime
import io
from ConfigParser import ConfigParser, MissingSectionHeaderError
import logging
# from webapp2_extras import i18n

# load modules defined by this app


SKY_URL = "http://dmfile.curitel.com/self_binary/sky_binary/real/download.inf"


class A820LHandler(RequestHandler):
    '''
    classdocs
    '''
    def get(self):
        try:
            content = fetch(SKY_URL).content
            config = ConfigParser()
            config.readfp(io.BytesIO(content))

            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            title = "A820L Firmware - Unknown @ (GAE) %s" % (timestamp)
            message = "version not available"
            if config.has_section("IM-A820L"):
                version = config.get("IM-A820L", "Version")
                if version != "S1231153":
                    title = "A820L Firmware - NEW @ (GAE) %s" % (timestamp)
                    body = "new version available: %s" % (version)
                else:
                    title = "A820L Firmware - OLD @ (GAE) %s" % (timestamp)
                    body = "still old version %s" % (version)

            # send email notification
            message = mail.EmailMessage()
            message.sender = "dantifer@gmail.com"
            message.subject = title
            message.to = "zfdang@freewheel.tv"
            message.body = body
            message.send()
            logging.info("Email sent: title = %s, content = %s" % (title, body))

        except InvalidURLError as e:
            # fetch error
            logging.error("A820LHandler urlfetch.fetch exception %s" % (e))
        except MissingSectionHeaderError as e:
            # ConfigParser error
            logging.error("A820LHandler ConfigParser.read exception %s" % (e))

    def post(self):
        pass


##########################################################
# define routers
routes = [
          Route('/tasks/a820l', handler='tasks.A820LHandler', name="tasks.a820l"),
          ]

application = webapp2.WSGIApplication(routes, debug=True)


# main goes here
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
