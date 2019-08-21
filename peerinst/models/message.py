# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from .student import Student
from .teacher import Teacher


class UserType(models.Model):
    type = models.CharField(max_length=32)

    def __unicode__(self):
        return self.type


class SaltiseMember(models.Model):
    name = models.CharField(max_length=64)
    picture = models.ImageField(blank=True, null=True, upload_to="images")

    def __unicode__(self):
        return self.name


class MessageType(models.Model):
    type = models.CharField(max_length=32)
    removable = models.BooleanField(default=True)
    colour = models.CharField(max_length=7)

    def __unicode__(self):
        return self.type


class Message(models.Model):
    type = models.ForeignKey(MessageType)
    authors = models.ManyToManyField(SaltiseMember)
    title = models.CharField(max_length=128)
    text = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    link = models.URLField(blank=True, null=True)
    for_users = models.ManyToManyField(UserType)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        for_users = [t.type for t in self.for_users.all()]
        if "teacher" in for_users:
            for teacher in Teacher.objects.all():
                UserMessage.objects.create(user=teacher.user, message=self)
        if "student" in for_users:
            for student in Student.objects.all():
                UserMessage.objects.create(user=student.student, message=self)


class UserMessage(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
