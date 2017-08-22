#!/usr/bin/python
#-*- coding:utf-8 -*-
import json
from io import BytesIO
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from utils.check_code import create_validate_code
from repository import models
from ..forms.account import LoginForm,RegisterForm

def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())


def login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        result = {'status': False, 'message': None, 'data': None}
        print(request.POST)
        # <QueryDict: {'csrfmiddlewaretoken': ['BKG8fs17VsqFj7z5Os19HAY1cmqUXa1mVnUXEvMFxWK8ZVF0WJKMVidfKHWNOHJx'], 'username': ['root'], 'password': ['Oldboyhaha!123'], 'check_code': ['h7x5'], 'rmb': ['1']}>

        form = LoginForm(request=request, data=request.POST)

        if form.is_valid():
            print(form.cleaned_data.get('rmb'))  # 1
            username = form.cleaned_data.get('username')
            print(username) # root
            password = form.cleaned_data.get('password')
            print(password) # Oldboyhaha!123
            user_info = models.UserInfo.objects. \
                filter(username=username, password=password). \
                values('nid', 'nickname',
                       'username', 'email',
                       'avatar',
                       'blog__nid',
                       'blog__site').first()


            if not user_info:
                # result['message'] = {'__all__': '用户名或密码错误'}
                result['message'] = '用户名或密码错误'
            else:
                result['status'] = True
                # 设置要返回给用户的sessionid号码，方便他下次过来携带登录验证
                request.session['user_info'] = user_info
                print(user_info) # {'nid': 1, 'nickname': '武沛齐', 'username': 'root', 'email': 'wupeiqi@live.com', 'avatar': 'static/imgs/avatar/20130809170025.png', 'blog__nid': 1, 'blog__site': 'wupeiqi'}
                if form.cleaned_data.get('rmb'):
                    request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    pass
        else:
            print(form.errors)
            if 'check_code' in form.errors:
                result['message'] = '验证码错误或者过期'
            else:
                result['message'] = '用户名或密码错误'
        print(result)
        return HttpResponse(json.dumps(result))

def register(request):
    '''
    注册
    :param request:
    :return:
    '''
    result = {'status': False, 'message': None, 'data': None}
    if request.method == 'GET':
        return render(request,'register.html')
    elif request.method == 'POST':
            print(request.POST)

            form = RegisterForm(request=request, data=request.POST)
            if form.is_valid():

                print(form.cleaned_data.get('check_code'))
                print(form.cleaned_data)
                username = form.cleaned_data['username']
                print(username)
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']
                models.UserInfo.objects.create(username=username,
                                               password=password,
                                               email=email,
                                               )
                result['status'] = True
            else:
                print(form.errors)
                if 'username' in form.errors:
                    result['message']='用户已存在请重新输入'

                elif '__all__' in form.errors:
                    result['message'] = '两次输入密码不一致'

                elif 'check_code' in form.errors:
                    result['message'] = '验证码错误或者过期'

                else:
                    result['message'] = '用户名或密码错误'
    print(result)

    return HttpResponse(json.dumps(result))






def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.clear()

    return redirect('/')


