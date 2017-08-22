#!/usr/bin/python
#-*- coding:utf-8 -*-
from django.shortcuts import HttpResponse,render,redirect

from django.urls import reverse
from repository import models
from utils.pagination import Pagination

from ..auth.auth import check_login

from ..forms.article import ArticleForm

import json
import uuid
import os
import sys
from django.http import JsonResponse


def check_login(func):
    def inner(request,*args,**kwargs):
        if request.session.get('user_info'):
            return func(request,*args,**kwargs)
        else:
            return redirect('/login.html')
    return inner



@check_login
# index = check_login(index) #程序启动之后就会加载这些check_login和index 函数此时就会执行到
# index = inner处；这时如果有用户访问index 函数就会触发index(request),此时就是会执行
# inner(request)函数，此时就会回到装饰器函数中去去执行：def inner(request,*args,**kwargs):
# 若返回的结果是：func(request,*args,**kwargs) 则就相当于执行index(request,*args,**kwargs)函数本身了；
def index(request,):
    upload_avatar = request.session.get('user_info')['avatar']
    return render(request,'backend_index.html',{'upload_avatar':upload_avatar})



@check_login

def article(request,*args,**kwargs):
    '''
    博主个人博客后台管理
    :param request:
    :param args:
    :param kwargs:
    :return:
    '''
    print(kwargs)
    blog_id = request.session.get('user_info')['blog__nid']
    upload_avatar = request.session.get('user_info')['avatar']
    print(blog_id)
    print(upload_avatar)
    #  对传入的参数列表按照自己的意愿进行字典类型的转化
    condition = {}
    for k ,v in kwargs.items():
        if v == '0':
            pass
        else:
            condition[k]=v
    condition['blog_id']=blog_id

    data_count = models.Article.objects.filter(**condition).count()
    print(data_count)
    page = Pagination(request.GET.get('p',1),data_count)
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    page_str = page.page_str(reverse('article',kwargs=kwargs))
    category_list = models.Category.objects.filter(blog_id=blog_id).values('nid','title')
    print(category_list)
    type_list = map(lambda item:{'nid':item[0],'title':item[1]},models.Article.type_choices)
    # type_list 目前还只是一个迭代器对象要执行可以使用list(type_list)
    kwargs['p']=page.current_page

    return  render(
        request,
        'backend_article.html',
        {   'upload_avatar':upload_avatar,
            'arg_dict':kwargs,
            'result':result,
            'page_str':page_str,
            'category_list':category_list,
            'type_list':type_list,
            'data_count':data_count,

        },
    )

@check_login
def add_article(request):
    '''
    增添文章
    :param request:
    :return:
    '''
    if request.method =='GET':
        upload_avatar = request.session.get('user_info')['avatar']
        print(request) # <WSGIRequest: GET '/backend/add-article.html'>
        print(request.session['user_info'])
        form = ArticleForm(request=request)
        return render(request,'backend_add_article.html',{'form':form,'upload_avatar':upload_avatar},)
    elif request.method == 'POST':
        upload_avatar = request.session.get('user_info')['avatar']
        print('heool')
        print(request.POST)
        form = ArticleForm(request,request.POST)
        if form.is_valid():
            print('你好')
            print(form.cleaned_data)
            tags = form.cleaned_data.pop('tags')
            print(type(tags[0])) # <class 'str'>
            print(type(tags))  # <class 'list'>
            content = form.cleaned_data.pop('content')
            form.cleaned_data['blog_id']=request.session['user_info']['blog__nid']
            obj = models.Article.objects.create(**form.cleaned_data)
            models.ArticleDetail.objects.create(content=content,article=obj)
            tag_list = []
            for tag_id in tags:
                # 将 标签表中的字符串类型转化成数字类型
                tag_id = int(tag_id)
                tag_list.append(models.Article2Tag(article_id=obj.nid,tag_id=tag_id))
            print('表亲列表')
            print(tag_list)  #[<Article2Tag: Article2Tag object>, <Article2Tag: Article2Tag object>]
            # for i in tag_list:
            #     print(i.article.title,i.tag.title) # 阿打算 HTML ;阿打算 HTML

            # def bulk_create(self, objs, batch_size=None):
            #     # 批量插入
            #     # batch_size表示一次插入的个数
            #     objs = [
            #         models.DDD(name='r11'),
            #         models.DDD(name='r22')
            #     ]
            #     models.DDD.objects.bulk_create(objs, 10)
            models.Article2Tag.objects.bulk_create(tag_list)

            return redirect('/backend/article-0-0.html')
        else:
            return render(request,'backend_add_article.html',{'form':form,'upload_avatar':upload_avatar})

    else:
        return redirect('/')


@check_login
def edit_article(request,nid):
    '''
    编辑文章
    :param request:
    :param nid:
    :return:
    '''
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid,blog_id=blog_id).first()
        # print(type(obj)) #<class 'django.db.models.query.QuerySet'>,此时是没有first()
        print(type(obj)) # <class 'repository.models.Article'>,此时才是一个文章对象
        if not obj:
            return render(request,'backend_no_article.html',{'obj':obj})

        tags = obj.tags.values_list('nid','title')
        print(tags) # <QuerySet [(1, 'HTML'), (2, '孤独者的python之路')]>
        if tags:
            tags = list(zip(*tags))[0]
            print(tags) #(1, 2)

        init_dict = {
            'nid':obj.nid,
            'title':obj.title,
            'summary':obj.summary,
            'category_id':obj.category_id,
            'article_type_id':obj.article_type_id,
            'content':obj.articledetail.content,
            'tags':tags,
        }
        #  'content':obj.articledetail.content, 反跨的代表
        form = ArticleForm(request=request,data=init_dict)
        return  render(request,'backend_editor_article.html',{'form':form,'nid':nid})

    elif request.method == 'POST':
        form = ArticleForm(request,request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request,'backend_no_article.html',)
            content = form.cleaned_data.pop('content')
            tags = form.cleaned_data.pop('tags')
            models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
            models.ArticleDetail.objects.filter(article=obj).update(content=content)
            models.Article2Tag.objects.filter(article=obj).delete()
            tag_list = []
            for tag_id in tags:
                tag_id = int(tag_id)
                tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
            models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_editor_article.html', {'form': form, 'nid': nid})

@check_login
def del_article(request,nid):
    '''
    删除文章
    :param request:
    :param nid:
    :return:
    '''
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        models.Article.objects.filter(blog_id=blog_id,nid=nid).delete()
    return redirect('/backend/article-0-0.html')

@check_login
def base_info(request):
    '''
    博主个人信息修改
    :param request:
    :return:
    '''
    upload_avatar = request.session.get('user_info')['avatar']
    username = request.session['user_info']['username']
    print(username)
    user = models.UserInfo.objects.filter(username=username).first()
    blog_id = request.session['user_info']['blog__nid']
    print(blog_id)
    blog = models.Blog.objects.filter(nid=blog_id).first()
    if request.method == 'GET':

        return render(request,'backend_base_info.html',{'user':user,'blog':blog,'upload_avatar':upload_avatar})

    elif request.method == 'POST':
        print(request.POST)
        name = request.POST.get('username')
        print(name)
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        site = request.POST.get('site')
        title = request.POST.get('title')
        print(email,nickname,site,title)

        models.UserInfo.objects.filter(username=username).update(
            username = name,
            nickname = nickname,
            email = email,
        )
        models.Blog.objects.filter(nid = blog_id).update(
            title = title,
            site = site,
        )

        return redirect('/backend/index.html')
    else:
        return redirect('/')


@check_login
def tag(request):
    '''
    标签管理
    :param request:
    :return:
    '''
    upload_avatar = request.session.get('user_info')['avatar']
    print(request.session['user_info'])
    blog_id = request.session['user_info']['blog__nid']
    print(blog_id)
    tags = models.Tag.objects.filter(blog_id=blog_id).all()
    print(tags)
    for i in tags:
        print(i)


    return render(request,'backend_tag.html' ,{'tags':tags,'upload_avatar':upload_avatar})

@check_login
def category(request):
    '''
    分类信息
    :param request:
    :return:
    '''
    upload_avatar = request.session.get('user_info')['avatar']
    blog_id = request.session['user_info']['blog__nid']
    print(blog_id)
    category_list = models.Category.objects.filter(blog_id=blog_id).all()
    print(category_list)
    for row in category_list:
        # print(row.title)
        # print(row.nid)
        a =models.Article.objects.filter(blog_id=blog_id,category=row.nid).count()
        print(a)
    # a = list(zip(*category_list))[0]
    # category = list(zip(*category_list))[1]
    # print(type(a))
    #
    # for j in a:
    #     print(j,type(j))
    #

    return render(request,'backend_category.html',{'category_list':category_list,'a':a,'upload_avatar':upload_avatar})


@check_login
def upload_avatar(request):
    user = request.session['user_info']
    print(user)
    username = request.session['user_info']['username']
    pic = models.UserInfo.objects.filter(username=username).first()
    print(pic.avatar)

    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        print(request.FILES)
        file_obj = request.FILES.get('avatar_img')
        print(file_obj) # 获取到的是这个图片信息的对象：名称是这个上传的图片的名称
        if not file_obj:
            pass
        else:
            file_name = str(uuid.uuid4())
            file_path = os.path.join('static/imgs/avatar', file_name)

            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path
            print(ret['data'])
            models.UserInfo.objects.filter(username=username).update(avatar = file_path)

    return HttpResponse(json.dumps(ret))


def addcomment(request):
    '''
    增加评论信息
    :param request:
    :return:
    '''
    ret = {'status':True,'message':None}
    user = request.session['user_info']
    print(user)

    if request.method == 'POST':
        print(request.FILES)
        file_obj = request.FILES.get('imgFile')
        if file_obj:
            print(file_obj) # 获取到的是这个图片信息的对象：名称是这个上传的图片的名称
            file_name = str(uuid.uuid4())
            file_path = 'static/imgs/comments'+'/'+file_name
            print(file_path)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            print(type(file_path))
            # 通过字符串拼接来实现join 的“\”的问题
            temp = '/'+file_path
            dic = {
                'error': 0,
                'url': temp,
                'message': '错误了...',
            }

            return JsonResponse(dic)
        else:
            user_id = request.session['user_info']['nid']
            print(user_id)
            print(request.POST)
            print(request.POST.get('user_id'))
            article_id = request.POST.get('nid')
            content = request.POST.get('comment_data')
            print(content)
            models.Comment.objects.create(
                content = content,
                article_id=article_id,
                user_id = user_id
            )
            article_obj = models.Article.objects.filter(nid=article_id).first()
            temp = article_obj.comment_count +1
            article_obj.comment_count = temp
            models.Article.objects.filter(nid=article_id).update(comment_count = temp)



            return JsonResponse(ret)



































