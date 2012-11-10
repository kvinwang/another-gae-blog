'''
BaseRequestHandler, some common job for all RequestHandler will be put here

Created on 2012-11-10

@author: DANG Zhengfa
'''
import webapp2
import logging
from webapp2_extras import i18n
from config import Configuration


AVAILABLE_LOCALES = ['zh_CN', 'en_US', 'es_ES']


class BaseRequestHandler(webapp2.RequestHandler):
    def __init__(self, request, response):
        """
        Override the initialiser in order to set the language.
        """
        self.initialize(request, response)

        # honor global settings first
        if "locale" in Configuration:
            locale = Configuration["locale"]
            i18n.get_i18n().set_locale(locale)
            logging.info("BaseRequestHandler: find locale from config - %s" % (locale))
        else:
            # first, try and set locale from cookie
            locale = request.cookies.get('locale')
            if locale in AVAILABLE_LOCALES:
                i18n.get_i18n().set_locale(locale)
                logging.info("BaseRequestHandler: find locale from cookie - %s" % (locale))
            else:
                # if that failed, try and set locale from accept language header
                header = request.headers.get('Accept-Language', '')  # e.g. en-gb,en;q=0.8,es-es;q=0.5,eu;q=0.3
                logging.info("BaseRequestHandler: header = %s" % (header))
                locales = [locale.split(';')[0] for locale in header.split(',')]
                for locale in locales:
                    if locale in AVAILABLE_LOCALES:
                        i18n.get_i18n().set_locale(locale)
                        response.set_cookie("locale", locale)
                        logging.info("BaseRequestHandler: find locale from langs - %s" % (locale))
                        break
                else:
                    # if still no locale set, use the first available one
                    i18n.get_i18n().set_locale(AVAILABLE_LOCALES[0])
                    response.set_cookie("locale", AVAILABLE_LOCALES[0])
                    logging.info("BaseRequestHandler: use default locale - %s" % (AVAILABLE_LOCALES[0]))
                    # response.set_cookie("userid", userid, expires=datetime.datetime.now()+datetime.timedelta(days=60),
                    #                     path="/", domain='zfdang.com', secure=False)
