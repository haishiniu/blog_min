#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.conf.urls import url
from .views import home
from .views import account

urlpatterns = [

    url(r'^laoren.html$',home.laoren),
    url(r'^login.html$', account.login),
    url(r'^logout.html$', account.logout),
    url(r'^register.html$', account.register),
    url(r'^check_code.html$', account.check_code),
    url(r'^all/(?P<article_type_id>\d+).html$', home.index, name='index'),
    url(r'^(?P<site>\w+).html$', home.home),
    url(r'^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', home.filter),
    url(r'^(?P<site>\w+)/(?P<nid>\d+).html$', home.detail),
    url(r'^addfavor.html',home.addfavor),
    url(r'^adddislike.html',home.adddislike),
    url(r'^', home.index),
]