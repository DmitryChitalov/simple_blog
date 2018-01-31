# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from blog.models import Post
from blog.models import Subscribes
from blog.models import NewsFeed
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.list import ListView

from blog.forms import PostForm

from django.http import HttpResponseRedirect

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from blog.models import Post
from profile.models import Profile
from django.contrib.auth.models import User

from django.views import View

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

import logging
logger = logging.getLogger(__name__)
from django.conf import settings

from django.views.generic.base import ContextMixin	

from django.core.mail import EmailMessage

##############Сохранение номера страницы в переменной pn##########
class PageNumberMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(PageNumberMixin, self).get_context_data(**kwargs)
        try:
            context["pn"] = self.request.GET["page"]
        except:
            context["pn"] = "1"
        return context
##################################################################

################Добавляем блог в список подписок##################
class SubscribeSave(View):	
    def post(self, request, *args, **kwargs):
        author = User.objects.get(id=request.user.id)
        blog = User.objects.get(id=self.kwargs["id"])
		
        subscribe = Subscribes.objects.filter(blog=blog)
        if subscribe:
            messages.add_message(request, messages.WARNING, "Вы уже подписаны на этот блог")
        else:
            subscribe = Subscribes.objects.create(user=author, blog=blog)
            messages.add_message(request, messages.SUCCESS, "Вы подписались на этот блог")

        redirect_url = reverse("post_list", kwargs = {"id": blog.id})
        return redirect(redirect_url)
##################################################################

#################Удаляем блог из списка подписок##################	
class UnSubscribeSave(View):
    def post(self, request, *args, **kwargs):
        author = User.objects.get(id=request.user.id)
        blog = User.objects.get(id=self.kwargs["id"])
        posts_list = Post.objects.filter(user=blog)
        subscribe = Subscribes.objects.filter(blog=blog).delete()
		
        NewsFeed.objects.filter(user=author, post__in=posts_list).delete()
        messages.add_message(request, messages.SUCCESS, "Вы отписались от блога пользователя: " + str(blog))
        redirect_url = reverse("blog_list")
        return redirect(redirect_url)           
##################################################################
      
#########Вывод списка постов для блога текущего пользователя#######
class CurrentUserPostListView(ArchiveIndexView):
    model = Post
    date_field = "posted"
    template_name = "mainpage.html"
    #paginate_by = 2
    allow_empty = True
    allow_future = True
    def get_context_data(self, **kwargs):
        context = super(CurrentUserPostListView, self).get_context_data(**kwargs)
        author = User.objects.get(id=self.request.user.id)
        posts_list = Post.objects.filter(user=self.request.user)
        paginator = Paginator(posts_list, 2)
        page = self.request.GET.get('page')	
		
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            page = int(page) - 1
            posts = paginator.page(page)

        context["posts"] = posts
        context["author"] = author
        return context
##################################################################

############Вывод списка постов для выбранного блога##############
class PostListView(ArchiveIndexView):
    model = Post
    date_field = "posted"
    template_name = "mainpage.html"
    allow_empty = True
    allow_future = True
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        author = User.objects.get(id=self.request.user.id)
        blog = User.objects.get(id=self.kwargs["id"])

        subscribe = Subscribes.objects.filter(user=author, blog=blog)
        if subscribe:
            context["is_subscribed"] = True
        else:
            context["is_subscribed"] = False
        context["blog"] = blog
        posts_list = Post.objects.filter(user = blog.id)
        paginator = Paginator(posts_list, 2)
        page = self.request.GET.get('page')	
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        context["posts"] = posts
        return context
##################################################################

####################Создание новой записи блога###################
class PostCreate(CreateView):
    fields = '__all__'
    model = Post
    template_name = "post_create.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Пост успешно добавлен")
        form.instance.user = self.request.user
        return super(PostCreate, self).form_valid(form)
##################################################################

#############Вывод содержимого любого поста любого блога##########
class PostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        author = User.objects.get(id=self.request.user.id)
        post = Post.objects.get(pk=self.kwargs["pk"])	
        if author != post.user:
            new_feed = NewsFeed.objects.filter(user=author, post=post, is_read=False)
            if new_feed:
                context["read_btn"] = True
        return context            			
##################################################################

##############Вывод содержимого прочитанного поста################
class ReadPostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    def get_context_data(self, **kwargs):
        context = super(ReadPostDetailView, self).get_context_data(**kwargs)
        author = User.objects.get(id=self.request.user.id)
        post = Post.objects.get(pk=self.kwargs["pk"])
        new_feed = NewsFeed.objects.filter(user=author, post=post).update(is_read=True)
        context["is_read"] = True      
        return context
##################################################################

#####################Обновление содержимого поста#################	
class PostUpdate(TemplateView, PageNumberMixin):
    post = None
    template_name = "post_edit.html"
    form = None
    def get(self, request, *args, **kwargs):
        self.post = Post.objects.get(pk = self.kwargs["pk"])
        self.form = PostForm(instance = self.post)
        return super(PostUpdate, self).get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data(**kwargs)
        context["post"] = self.post
        context["form"] = self.form
        return context
    def post(self, request, *args, **kwargs):
        self.post = Post.objects.get(pk = self.kwargs["pk"])
        self.form = PostForm(request.POST, instance = self.post)
        if self.form.is_valid():
            self.form.save()
            messages.add_message(request, messages.SUCCESS, "Пост успешно изменен")
            redirect_url = reverse("index")+ "?page=" + self.request.GET["page"]
            return redirect(redirect_url)
        else:
            return super(PostUpdate, self).get(request, *args, **kwargs)
##################################################################

###########################Удаление поста#########################
class PostDelete(TemplateView, PageNumberMixin):
    post = None
    template_name = "post_delete.html"
    form = None
    def get(self, request, *args, **kwargs):
        self.post = Post.objects.get(pk = self.kwargs["pk"])
        return super(PostDelete, self).get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(PostDelete, self).get_context_data(**kwargs)
        context["post"] = self.post
        return context
    def post(self, request, *args, **kwargs):
        self.post = Post.objects.get(pk = self.kwargs["pk"])
        self.post.delete()
        messages.add_message(request, messages.SUCCESS, "Пост успешно удален")		
        redirect_url = reverse("index") + "?page=" + self.request.GET["page"]		
        return redirect(redirect_url)
##################################################################

###########################Вывод cписка блогов####################
class BlogsListView(ListView):
    model = Profile
    template_name = 'blogslist.html'
    def get_queryset(self):
        users = Profile.objects.all().exclude(user=self.request.user.id)
        return users
##################################################################
from django.contrib.auth.models import User
#########################Вывод новостной ленты####################	
class NewsView(ArchiveIndexView, PageNumberMixin):
    model = NewsFeed
    date_field = "posted"
    template_name = "news.html"
    allow_empty = True
    allow_future = True		
    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        author = User.objects.get(id=self.request.user.id)
        author_subscribes = Subscribes.objects.filter(user=author)
        sub_names = []
        for sub in author_subscribes:
			###собираем имена авторов блогов, на которые подписаны
            sub_names.append(sub.blog)
		###собираем посты блогов, на которые подписаны
        sub_news = Post.objects.filter(user__in=sub_names)		
        for sub_new in sub_news:
            news_feed = NewsFeed.objects.filter(user=author, post=sub_new)
            if not news_feed:
                news_feed = NewsFeed.objects.create(user=author, post=sub_new, posted=sub_new.posted)
				
                ctx = {
                    'news_feed': news_feed,				
                }
				
                users = User.objects.all()
                emails_list = []
                for user in users:
                    email = str(user.email)
                    if email != "":
                        emails_list.append(email)

                recipient_list = emails_list
                message = get_template('email.html').render(ctx)
                msg = EmailMessage('Обновление ленты', message, from_email=settings.EMAIL_HOST_USER, to=recipient_list)
                msg.content_subtype = 'html'
                msg.send(fail_silently=True)
              
        newsfeeds_list = NewsFeed.objects.filter(user=author)
		
        paginator = Paginator(newsfeeds_list, 2)
        page = self.request.GET.get('page')	
        try:
            newsfeeds = paginator.page(page)
        except PageNotAnInteger:
            newsfeeds = paginator.page(1)
        context["newsfeeds"] = newsfeeds
        return context
##################################################################	
