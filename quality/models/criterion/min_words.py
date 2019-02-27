# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.utils import IntegrityError

from .criterion import Criterion, CriterionExistsError


class MinWordsCriterion(Criterion):
    name = models.CharField(max_length=32, default="min_words", editable=False)
    min_words = models.PositiveIntegerField(unique=True)

    def evaluate(self, answer):
        return len(answer.rationale.split()) >= self.min_words

    @staticmethod
    def create(min_words):
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
        if min_words < 0:
            raise ValueError("The minmum number of words can't be negative.")
        try:
            criterion = MinWordsCriterion.objects.create(
                name="min_words", min_words=min_words
            )
        except IntegrityError:
            raise CriterionExistsError()
        return criterion
