# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.utils import IntegrityError

from .criterion import Criterion, CriterionExistsError


class MinCharsCriterion(Criterion):
    name = models.CharField(max_length=32, default="min_chars", editable=False)

    @staticmethod
    def info():
        return {
            "name": "min_chars",
            "full_name": "Min characters",
            "description": "Imposes a minium number of characters for each "
            "rationale.",
        }

    def evaluate(self, answer, rules_pk):
        rules = MinCharsCriterionRules.objects.get(pk=rules_pk)
        return len(answer.rationale) >= rules.min_chars

    def serialize(self, rules_pk):
        rules = MinCharsCriterionRules.objects.get(pk=rules_pk)
        data = dict(rules)
        data = {rule: data[rule] for rule in self.rules}
        data.update({"version": self.version, "is_beta": self.is_beta})
        return data


class MinCharsCriterionRules(models.Model):
    min_chars = models.PositiveIntegerField(unique=True)

    @staticmethod
    def create(min_chars):
        """
        Creates the criterion version.

        Parameters
        ----------
        min_words : int >= 0
            Minimum number of words for the quality to evaluate to True.

        Returns
        -------
        MinWordsCriterion
            Created instance

        Raises
        ------
        ValueError
            If the arguments have invalid values
        CriterionExistsError
            If a criterion with the same options already exists
        """
        if min_chars < 0:
            raise ValueError(
                "The minmum number of characters can't be negative."
            )
        try:
            criterion = MinCharsCriterionRules.objects.create(
                min_chars=min_chars
            )
        except IntegrityError:
            raise CriterionExistsError()
        return criterion
