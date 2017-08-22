#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.conf.urls import url

from .views import user

urlpatterns = [
    url(r'^index.html$',user.index),
    url(r'^article-(?P<article_type_id>\d+)-(?P<category_id>\d+).html',user.article,name='article'),
    url(r'^base-info.html$', user.base_info),
    url(r'^tag.html$', user.tag),
    url(r'^category.html$', user.category),
    url(r'^add-article.html',user.add_article),
    url(r'^edit-article-(?P<nid>\d+).html$', user.edit_article),
    url(r'^del-article-(?P<nid>\d+).html$',user.del_article),
    url(r'^upload-avatar.html$', user.upload_avatar),
    url(r'^addcomment.html$',user.addcomment),
]
