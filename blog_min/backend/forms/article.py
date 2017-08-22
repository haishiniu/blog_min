#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.core.exceptions import ValidationError

from django import forms as django_forms

from django.forms import fields as django_fields

from django.forms import widgets as django_widgets
from repository import models

class ArticleForm(django_forms.Form):
    title =django_fields.CharField(
        widget=django_widgets.TextInput(attrs={'class':'form-control','placeholder':'文章标题'})

    )
    summary = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class':'form-control','placeholder':'文章简介','rows':'3'})
    )

    content  = django_fields.CharField(
        widget= django_widgets.Textarea(attrs={'class':'kind-content'})
    )

    article_type_id = django_fields.IntegerField(
        widget=django_widgets.RadioSelect(choices=models.Article.type_choices)
    )
    category_id = django_fields.ChoiceField(
        choices=[],
        widget=django_widgets.RadioSelect
    )

    tags = django_fields.MultipleChoiceField(
        choices=[],
        widget=django_widgets.CheckboxSelectMultiple
    )
    # 主要是为了实现数据库的实时更新（初始化函数中加上数据的获取）
    def __init__(self,request,*args,**kwargs):
        super(ArticleForm,self).__init__(*args,**kwargs)
        blog_id =request.session['user_info']['blog__nid']
        self.fields['category_id'].choices = models.Category.objects.filter(blog_id=blog_id).values_list('nid','title')
        print(self.fields['category_id']) #<django.forms.fields.ChoiceField object at 0x035E0B30>
        print(self.fields['category_id'].choices) # [(1, '.NET'), (2, '领域驱动'), (3, 'python'), (4, '设计模式'), (5, 'letCode')]
        self.fields['tags'].choices = models.Tag.objects.filter(blog_id=blog_id).values_list('nid','title')
