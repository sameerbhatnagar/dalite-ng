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
        if not hasattr(self, "name"):
            raise NotImplementedError(
                "Your criterion needs to have a `name` field. Make sure it's "
                "different from the others or it may lead to some trouble "
                "down the line."
            )
        super(Criterion, self).save(*args, **kwargs)

    def __iter__(self):
        return (
            (field.name, getattr(self, field.name))
            for field in self.__class__._meta.get_fields()
        )


class CriterionExistsError(Exception):
    def __init__(self, msg="", *args, **kwargs):
        if not msg:
            msg = "A criterion with the same options already exists."
        super(Exception, self).__init__(msg, *args, **kwargs)


class CriterionDoesNotExistError(Exception):
    def __init__(self, msg="", *args, **kwargs):
        if not msg:
            msg = (
                "There is no criterion corresponding to that name or version."
            )
        super(Exception, self).__init__(msg, *args, **kwargs)
