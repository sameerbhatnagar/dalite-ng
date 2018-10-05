# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.db import models
from jsonfield import JSONField


class FakeUsername(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("fake username")
        verbose_name_plural = _("fake usernames")


class FakeCountry(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("fake country")
        verbose_name_plural = _("fake countries")


class LtiEvent(models.Model):
    # question = models.ForeignKey(Question,blank=True,null=True)
    # assignment = models.ForeignKey(Assignment,blank=True,null=True)
    # user = models.ForeignKey(User,blank=True, null=True)
    event_type = models.CharField(max_length=100)
    event_log = JSONField(default={})
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return str(self.timestamp)
