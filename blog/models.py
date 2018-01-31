# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from profile.models import Profile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Post(models.Model):
    title = models.CharField(max_length = 100, unique_for_date = "posted", verbose_name = "Заголовок")
    content = models.TextField(verbose_name = "Текст")
    posted = models.DateTimeField(default = datetime.now(), verbose_name = "Время публикация")
    user = models.ForeignKey(User, editable = True, verbose_name = "Автор")
        
    class Meta:
        ordering = ["-id"]
        verbose_name = "статья блога"
        verbose_name_plural = "статьи блога"
		
    def __unicode__(self): 
        return "%s" % self.title
		
    def get_absolute_url(self):
        return reverse("post_detail", kwargs = {"pk": self.pk})	
		
class Subscribes(models.Model):
    user = models.ForeignKey(User, verbose_name = "Владелец блога")
    blog = models.ForeignKey(User, related_name = "blogs", verbose_name = "Блог по подписке")
	
    class Meta:
        ordering = ["user"]
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
		
class NewsFeed(models.Model):
    user = models.ForeignKey(User, verbose_name = "Владелец блога")
    post = models.ForeignKey(Post, related_name = "posts", verbose_name = "Пост ленты")
    posted = models.DateTimeField(db_index = True, verbose_name = "Время публикация")
    is_read = models.BooleanField(default=False, verbose_name = "Пометка о прочитанности")
	
    class Meta:
        ordering = ["user"]
        verbose_name = "пост подписки"
        verbose_name_plural = "посты подписки"
		
