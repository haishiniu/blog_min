#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.exceptions import ValidationError
from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets

from repository import models

from .base import BaseForm


class LoginForm(BaseForm, django_forms.Form):
    # username = django_fields.CharField(
    # min_length=6,
    # max_length=20,
    #     error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符", 'max_length': "用户名长度不能大于32个字符"}
    # )
    username = django_fields.CharField()

    # password = django_fields.RegexField(
    #     '^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
    #     min_length=12,
    #     max_length=32,
    #     error_messages={'required': '密码不能为空.',
    #                     'invalid': '密码必须包含数字，字母、特殊字符',
    #                     'min_length': "密码长度不能小于8个字符",
    #                     'max_length': "密码长度不能大于32个字符"}
    # )
    password = django_fields.CharField()
    rmb = django_fields.IntegerField(required=False)

    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    # 也就是俗称的钩子函数（需要查阅）
    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')


class RegisterForm(BaseForm, django_forms.Form):

    username = django_fields.CharField()

    email = django_fields.EmailField()

    password = django_fields.CharField()

    confirm_password = django_fields.CharField()

    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )


    def clean_username(self):
        if  models.UserInfo.objects.filter(username =self.request.POST.get('username')).first():
            raise ValidationError(message='用户已存在请重新输入',code='invalid')

        else:
            return self.request.POST.get('username')

    def clean(self):
        if self.request.POST.get('password')!= self.request.POST.get('confirm_password'):
            raise ValidationError(message='两次输入密码不一致',code='invalid')

    def clean_check_code(self):
        print(self.request.POST.get('password'))
        print(self.request.POST.get('confirm_password'))
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')

        else:
            return self.request.POST.get('check_code')



