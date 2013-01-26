# coding=UTF-8
# this file defines all langs supported by this app

AVAILABLE_LOCALES = ['zh_CN', 'en_US']
AVAILABLE_LOCALES_DESC = [u'简体中文', u'English(US)']


def getLangsList():
    langList = []
    for idx in range(0, len(AVAILABLE_LOCALES)):
        locale = AVAILABLE_LOCALES[idx]
        locale_desc = AVAILABLE_LOCALES_DESC[idx]
        ldict = {}
        ldict['locale'] = locale
        ldict['description'] = locale_desc
        langList.append(ldict)

    return langList
