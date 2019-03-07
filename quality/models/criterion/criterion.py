# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models

from ..quality_type import QualityType


class Criterion(models.Model):
    version = models.AutoField(primary_key=True)
    uses_rules = models.TextField(
        blank=True,
        help_text="Comma separated list of used rules for the criterion "
        "found as the fields of the associated rules object.",
    )
    is_beta = models.BooleanField(default=False)
    for_quality_types = models.ManyToManyField(QualityType)

    class Meta:
        abstract = True

    @staticmethod
    def info():
        raise NotImplementedError("This property has to be implemented.")

    def evaluate(self, answer, rules_pk):
        raise NotImplementedError("This property has to be implemented.")

    def serialize(self, rules_pk):
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
        self.uses_rules = re.sub(r"\s*,\s*", ", ", self.uses_rules)
        super(Criterion, self).save(*args, **kwargs)

    @property
    def rules(self):
        return self.uses_rules.split(", ")


class CriterionRules(models.Model):
    def __iter__(self):
        return (
            (field.name, getattr(self, field.name))
            for field in self.__class__._meta.get_fields()
        )

    @staticmethod
    def get_or_create(*args, **kwargs):
        raise NotImplementedError("This property has to be implemented.")
