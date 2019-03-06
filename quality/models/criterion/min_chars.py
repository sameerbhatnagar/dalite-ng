# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.utils import IntegrityError

from .criterion import Criterion, CriterionExistsError


class MinCharsCriterion(Criterion):
    name = models.CharField(max_length=32, default="min_chars", editable=False)
    min_chars = models.PositiveIntegerField(unique=True)

    def evaluate(self, answer):
        return len(answer.rationale) >= self.min_chars

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
            criterion = MinCharsCriterion.objects.create(
                name="min_chars", min_chars=min_chars
            )
        except IntegrityError:
            raise CriterionExistsError()
        return criterion

    @staticmethod
    def info():
        return {
            "name": "min_chars",
            "full_name": "Min characters",
            "description": "Imposes a minium number of characters for each "
            "rationale.",
        }
