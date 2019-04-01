# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django.db import models

from ..custom_fields import CommaSepField, ProbabilityField
from ..quality_type import QualityType


class Criterion(models.Model):
    version = models.AutoField(primary_key=True)
    uses_rules = CommaSepField(
        distinct=True,
        blank=True,
        help_text="Comma separated list of used rules for the criterion "
        "found as the fields of the associated rules object. Make sure to use "
        "the verbose_name",
    )
    is_beta = models.BooleanField(default=False)
    binary_threshold = models.BooleanField(default=False)
    for_quality_types = models.ManyToManyField(QualityType)

    class Meta:
        abstract = True

    @staticmethod
    def info():
        raise NotImplementedError("This method has to be implemented.")

    @staticmethod
    def create_default():
        raise NotImplementedError("This method has to be implemented.")

    def __iter__(self):
        """
        Any attribute specific to the criterion version (not in rules) should
        be added in the __iter__ method of the child model.
        You can use
        return itertools.chain(`child_iter`, Super(`Class`, self).__iter__())`
        to combine them.
        """
        return chain(
            self.__class__.info().iteritems(),
            {
                "version": self.version,
                "versions": [
                    {
                        "version": version.version,
                        "is_beta": version.is_beta,
                        "binary_threshold": version.binary_threshold,
                    }
                    for version in self.__class__.objects.all()
                ],
            }.iteritems(),
        )

    def evaluate(self, answer, rules_pk):
        raise NotImplementedError("This method has to be implemented.")

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

    @property
    def rules(self):
        return self.uses_rules


class CriterionRules(models.Model):
    threshold = ProbabilityField(
        verbose_name="Threshold",
        help_text="Minimum value for the answer to be accepted",
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_or_create(*args, **kwargs):
        raise NotImplementedError("This method has to be implemented.")

    def __iter__(self):
        return {
            field.name: {
                "name": field.name,
                "full_name": field.verbose_name,
                "description": field.help_text,
                "value": getattr(self, field.name),
                "type": field.__class__.__name__,
            }
            for field in self.__class__._meta.get_fields()
            if field.name != "id" and not field.name.endswith("ptr")
        }.iteritems()
