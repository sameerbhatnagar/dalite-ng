# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SaltiseMember(models.Model):
    name = models.CharField(max_length=64)
    picture = models.ImageField(blank=True, null=True, upload_to="images")


class MessageType(models.Model):
    type = models.CharField(max_length=32)
    removable = models.BooleanField(default=True)
    colour = models.CharField(max_length=7)


class Message(models.Model):
    type = models.ForeignKey(MessageType)
    title = models.CharField(max_length=128)
    text = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
