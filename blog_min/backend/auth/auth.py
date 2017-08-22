#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.shortcuts import redirect
# 做cookie 和session 的验证
def check_login(func):
    def inner(request,*args,**kwargs):
        if request.session.get('user_info'):
            return func(request,*args,**kwargs)
        else:
            return redirect('/login.html')
    return inner










