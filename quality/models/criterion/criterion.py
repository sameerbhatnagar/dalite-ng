# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Criterion(models.Model):
    version = models.AutoField(primary_key=True)

    class Meta:
        abstract = True

    def evaluate(self, answer):
        raise NotImplementedError("This property has to be implemented.")

    def save(self, *args, **kwargs):
        """
        Saves the new criterion making sure only one exists for each criterion
        name.
        """
        if self.name is None:
            raise NotImplementedError(
                "Your criterion needs to have a `name` field. Make sure it's "
                "different from the others or it may lead to some trouble "
                "down the line."
            )
        super(Criterion, self).save(*args, **kwargs)


class CriterionExistsError(Exception):
    def __init__(self):
        super(Exception, self).save(
            "A criterion with the same options already exists."
        )
