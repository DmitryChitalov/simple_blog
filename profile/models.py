# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Profile(models.Model):
    user = models.OneToOneField('auth.User', related_name='profile')
    full_name = models.CharField(verbose_name=u'ФИО', blank=True, null=True, max_length=255)
	
    def __unicode__(self): 
        return "%s" % self.full_name
	
    def __str__(self):
        return u'{:d}'.format(self.user_id)

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'