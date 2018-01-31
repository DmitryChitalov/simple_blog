# coding: utf-8

from django.conf.urls import url
from blog.views import PostListView, PostCreate, PostDetailView, PostUpdate, PostDelete, BlogsListView, SubscribeSave, UnSubscribeSave, NewsView, ReadPostDetailView
from django.contrib.auth.decorators import permission_required

urlpatterns = [
	url(r'^(?P<id>\d+)/posts/$', PostListView.as_view(), name="post_list"),
	url(r'^$', BlogsListView.as_view(), name="blog_list"),
    url(r'^add/$', PostCreate.as_view(), name = "post_add"),
    url(r'^(?P<pk>\d+)/detail/$', PostDetailView.as_view(), name = "post_detail"),	
	url(r'^(?P<pk>\d+)/postread/$', ReadPostDetailView.as_view(), name = "post_read"),
    url(r'^(?P<pk>\d+)/edit/$', PostUpdate.as_view(), name = "post_edit"),
    url(r'^(?P<pk>\d+)/delete/$', PostDelete.as_view(), name = "post_delete"), 
    url(r'^(?P<id>\d+)/subcribe/$', SubscribeSave.as_view(), name="subcribe"),
	url(r'^(?P<id>\d+)/unsubcribe/$', UnSubscribeSave.as_view(), name="unsubcribe"),
    url(r'^news/$', NewsView.as_view(), name = "news"),
]





