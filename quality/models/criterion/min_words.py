# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.utils import IntegrityError

from .criterion import Criterion, CriterionExistsError


class MinWordsCriterion(Criterion):
    name = models.CharField(max_length=32, default="min_words", editable=False)
    min_words = models.PositiveIntegerField()

    def evaluate(self, answer):
        return answer.rationale.split().length >= self.min_words

    @staticmethod
    def create(self, min_words):
        """
        Creates the criterion version.

        Parameters
        ----------
        min_words : int
            Minimum number of words for the quality to evaluate to True.

        Returns
        -------
        MinWordsCriterion
            Created instance

        Raises
        ------
        CriterionExistsError
            If a criterion with the same options already exists
        """
        try:
            criterion = MinWordsCriterion.objects.create(
                name="min_words", min_words=min_words
            )
        except IntegrityError:
            raise CriterionExistsError()
        return criterion
