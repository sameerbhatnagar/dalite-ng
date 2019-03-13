# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ..criterion import Criterion, CriterionRules


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


class MinCharsCriterionRules(CriterionRules):
    min_chars = models.PositiveIntegerField(
        verbose_name="Min characters",
        help_text="The minimum number of characters needed by a rationale.",
    )

    @staticmethod
    def get_or_create(min_chars=0):
        """
        Creates or get the criterion rules.

        Parameters
        ----------
        min_words : int >= 0 (default : 0)
            Minimum number of words for the quality to evaluate to True.

        Returns
        -------
        MinWordsCriterionRules
            Instance

        Raises
        ------
        ValueError
            If the arguments have invalid values
        """
        if min_chars < 0:
            raise ValueError(
                "The minmum number of characters can't be negative."
            )
        criterion, __ = MinCharsCriterionRules.objects.get_or_create(
            min_chars=min_chars
        )
        return criterion
