# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class QualityType(models.Model):
    type = models.CharField(max_length=32)
    model = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.type


class QualityUseType(models.Model):
    type = models.CharField(max_length=32)

    def __str__(self):
        return self.type
