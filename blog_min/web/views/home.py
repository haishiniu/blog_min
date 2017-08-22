#!/usr/bin/python
#-*- coding:utf-8 -*-

from django.shortcuts import render,redirect,HttpResponse
from repository import models
from utils.pagination import Pagination
from django.urls import  reverse
from django.http import JsonResponse

import json

def index(request,*args,**kwargs):
    '''
    博客的首页，用于展示全部的博文
    :param request:
    :param args:
    :param kwargs:
    :return:
    '''
    article_type_list = models.Article.type_choices
    print(kwargs,article_type_list)
    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        base_url = reverse('index',kwargs=kwargs)
        print(base_url)
    else:
        article_type_id = None
        base_url = '/'
    data_count = models.Article.objects.filter(**kwargs).count()
    print(data_count)

    print(request.GET.get('p'))
    page_obj = Pagination(request.GET.get('p'),data_count)
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)
    article_list_new = models.Article.objects.filter(**kwargs).order_by('-nid')[1:5]
    article_list_more = models.Article.objects.filter(**kwargs).order_by('-comment_count')[1:5]


    return render(
        request,
        'index.html',
        {
            'article_list_more':article_list_more,
            'article_list_new':article_list_new,
            'article_list': article_list,
            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'page_str': page_str,
        }
    )


def home(request,site):
    print(site)
    blog = models.Blog.objects.filter(site=site).first()
    print(type(blog))

    if not blog:
        return redirect('/')
    # 此处的blog=blog 实际是指blog_id
    tag_list = models.Tag.objects.filter(blog=blog).all()
    category_list = models.Category.objects.filter(blog=blog).all()
    date_list =models.Article.objects.raw(
        'select nid,count(nid) as num ,strftime("%Y-%m",create_time) as ctime from repository_article group by strftime("%Y-%m",create_time)'
    )

    article_list = models.Article.objects.filter(blog=blog).order_by('-nid').all()
    return render(
        request,
        'home.html',
        {
            'blog':blog,
            'tag_list':tag_list,
            'category_list':category_list,
            'date_list':date_list,
            'article_list':article_list,
        }

    )



def detail(request,site,nid):
    '''
     显示文章的详细信息
    :param request:
    :return:
    '''
    print(request.GET)
    print(request.POST)
    print(request.session.get('user_info'))
    user_info = request.session.get('user_info')
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw(
        'select nid,count(nid) as num ,strftime("%Y-%m",create_time) as ctime from repository_article group by strftime("%Y-%m",create_time)',

    )


    article = models.Article.objects.filter(blog=blog,nid=nid).select_related('category','articledetail').first()
    read_counts = models.Article.objects.filter(blog=blog,nid=nid).first().read_count
    temp = read_counts + 1
    models.Article.objects.filter(blog=blog,nid=nid).update(read_count=temp)
    comment_list = models.Comment.objects.filter(article=article).select_related('reply')
    return render(
        request,
        'home_detail.html',
        {
              'blog':blog,
              'tag_list':tag_list,
              'comment_list':comment_list,
              'date_list':date_list,
              'category_list':category_list,
              'article': article,
              'user_info':user_info
        },
    )



def filter(reqest,site,condition,val):
    '''
    自己博客的博文按照分类信息进行展示
    :param reqest:
    :param site:
    :param condition:
    :param val:
    :return:
    '''
    print(site,condition,val)
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Blog.objects.raw(
        'select nid,count(nid) as num ,strftime("%Y-%m",create_time) as ctime from repository_article group by strftime("%Y-%m",create_time)'
    )

    template_name = 'home_summary_list.html'
    if condition == 'tag':
        template_name = "home_title_list.html"
        article_list = models.Article.objects.filter(blog=blog,tags=val).all()

    elif condition == 'category':
        article_list = models.Article.objects.filter(blog=blog,category_id=val ).all()

    elif condition == 'date':
        # 此处要通过时间来筛选出文章信息，必须对时间进行一定的处理
        article_list = models.Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'],params=[val,]).all()
    else:
        article_list = []

    return render(
        reqest,
        template_name,
        {   'blog':blog,
            'tag_list':tag_list,
            'category_list':category_list,
            'date_list':date_list,
            'article_list':article_list,
        },

    )





def addfavor(request):
    print('我收到啦')
    ret = {'status':False,'data':None,'message':None}

    try:
        id = request.POST.get('nid')
        print(id)
        article = models.Article.objects.filter(nid=id).first()
        temp = article.up_count +1
        print(temp)
        article.up_count = temp
        models.Article.objects.filter(nid=id).update(up_count=temp)
        ret['status']= True
        ret['data']=temp
    # e 就是 Exception这个对象
    except Exception as e:
        ret['message'] = 'this option is invalid'

    result = json.dumps(ret)

    return HttpResponse(result)






def adddislike(request):
    print('我没有收到')
    ret = {'status':False,'data':None,'message':None}

    try:
        id = request.POST.get('nid')
        print(id)
        article = models.Article.objects.filter(nid=id).first()
        temp = article.down_count +1
        print(temp)
        article.down_count = temp
        models.Article.objects.filter(nid=id).update(down_count=temp)
        ret['status']= True
        ret['data']=temp
    # e 就是 Exception这个对象
    except Exception as e:
        ret['message'] = 'this option is invalid'

    result = json.dumps(ret)

    return HttpResponse(result)



def laoren(request):
    ret = {'status': '','msg': ""}
    print(request.POST)
    print(request.FILES)
    dic = {
        'error': 0,
        'url': '/static/imgs/4.jpg',
        'message': '错误了...'
    }

    return JsonResponse(dic)









