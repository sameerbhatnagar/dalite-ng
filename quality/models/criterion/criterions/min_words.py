# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ..criterion import Criterion, CriterionRules


class MinWordsCriterion(Criterion):
    name = models.CharField(max_length=32, default="min_words", editable=False)

    @staticmethod
    def info():
        return {
            "name": "min_words",
            "full_name": "Min words",
            "description": "Imposes a minium number of words for each "
            "rationale.",
        }

    def evaluate(self, answer, rules_pk):
        rules = MinWordsCriterionRules.objects.get(pk=rules_pk)
        return len(answer.rationale.split()) >= rules.min_words


class MinWordsCriterionRules(CriterionRules):
    min_words = models.PositiveIntegerField(
        verbose_name="Min words",
        help_text="The minimum number of words needed by a rationale.",
    )

    @staticmethod
    def get_or_create(min_words=0):
        """
        Creates or the criterion rules.

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
        if min_words < 0:
            raise ValueError("The minmum number of words can't be negative.")
        criterion, __ = MinWordsCriterionRules.objects.get_or_create(
            min_words=min_words
        )
        return criterion