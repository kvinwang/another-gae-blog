'''
Created on 2012-10-26

@author: DANG Zhengfa
'''
import datetime
from google.appengine.ext import db
from google.appengine.api import users

class Entry(db.Model):
    author = db.UserProperty()
    author_name = db.StringProperty()
    published = db.BooleanProperty(default=False)
    content = db.TextProperty(default='')
    readtimes = db.IntegerProperty(default=0)
    title = db.StringProperty(multiline=False,default='')
    date = db.DateTimeProperty(auto_now_add=True)
    mod_date = db.DateTimeProperty(auto_now_add=True)
    tags = db.StringListProperty()
    categorie_keys=db.ListProperty(db.Key)
    slug = db.StringProperty(multiline=False,default='')
    link= db.StringProperty(multiline=False,default='')
    monthyear = db.StringProperty(multiline=False)
    entrytype = db.StringProperty(multiline=False,default='post',choices=[
        'post','page'])
    entry_parent=db.IntegerProperty(default=0)#When level=0 show on main menu.
    menu_order=db.IntegerProperty(default=0)
    commentcount = db.IntegerProperty(default=0)
    trackbackcount = db.IntegerProperty(default=0)

    allow_comment = db.BooleanProperty(default=True) #allow comment
    #allow_pingback=db.BooleanProperty(default=False)
    allow_trackback = db.BooleanProperty(default=True)
    password=db.StringProperty()

    #compatible with wordpress
    is_wp=db.BooleanProperty(default=False)
    post_id= db.IntegerProperty()
    excerpt=db.StringProperty(multiline=True)

    #external page
    is_external_page=db.BooleanProperty(default=False)
    target=db.StringProperty(default="_self")
    external_page_address=db.StringProperty()

    #keep in top
    sticky=db.BooleanProperty(default=False)


    postname=''
    _relatepost=None

    @property
    def content_excerpt(self):
        return self.get_content_excerpt(_('..more').decode('utf8'))



class Category(db.Model):
    uid=db.IntegerProperty()
    name=db.StringProperty(multiline=False)
    slug=db.StringProperty(multiline=False)
    parent_cat=db.SelfReferenceProperty()

class Link(db.Model):
    title=db.StringProperty(required=True)
    target=db.StringProperty(required=True)
    sequence = db.IntegerProperty(required=True)
    date=db.DateTimeProperty(auto_now_add=True)
    updated_at=db.DateTimeProperty()

