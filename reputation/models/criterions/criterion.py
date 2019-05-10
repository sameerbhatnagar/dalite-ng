# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django.db import models

from ..reputation_type import ReputationType


class Criterion(models.Model):
    version = models.AutoField(primary_key=True)
    for_reputation_types = models.ManyToManyField(ReputationType)

    class Meta:
        abstract = True

    def evaluate(self, model):
        raise NotImplementedError("This method has to be implemented.")

    def save(self, *args, **kwargs):
        """
        Saves the new criterion making sure the `name` field exists.
        """
        if not hasattr(self, "name"):
            raise NotImplementedError(
                "Your criterion needs to have a `name` field. Make sure it's "
                "different from the others or it may lead to some trouble "
                "down the line."
            )
        super(Criterion, self).save(*args, **kwargs)

    @staticmethod
    def info():
        raise NotImplementedError("This method has to be implemented.")

    @staticmethod
    def create_default():
        raise NotImplementedError("This method has to be implemented.")
