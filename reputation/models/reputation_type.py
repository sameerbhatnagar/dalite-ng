# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class ReputationType(models.Model):
    type = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.type

    def evaluate(self):
        pass
