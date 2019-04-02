# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from quality.models.quality_type import QualityType

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

    @staticmethod
    def create_default():
        criterion = MinCharsCriterion.objects.create(uses_rules="min_chars")
        criterion.for_quality_types.add(
            QualityType.objects.get(type="assignment"),
            QualityType.objects.get(type="group"),
            QualityType.objects.get(type="teacher"),
            QualityType.objects.get(type="global"),
        )
        criterion.save()
        return criterion

    def evaluate(self, answer, rules_pk):
        if not isinstance(answer, basestring):
            answer = answer.rationale
        rules = MinCharsCriterionRules.objects.get(pk=rules_pk)
        evaluation = {
            "version": self.version,
            "quality": float(len(answer.replace(" ", "")) >= rules.min_chars),
        }
        evaluation.update(
            {criterion: val["value"] for criterion, val in rules}
        )
        return evaluation


class MinCharsCriterionRules(CriterionRules):
    min_chars = models.PositiveIntegerField(
        verbose_name="Min characters",
        help_text="The minimum number of characters needed by a rationale.",
    )

    def __str__(self):
        return "Rules {} for criterion min_chars".format(self.pk)

    @staticmethod
    def get_or_create(threshold=1, min_chars=0):
        """
        Creates or get the criterion rules.

        Parameters
        ----------
        threshold : float in [0, 1] (default : 0)
            Minimum value for the criterion to pass
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
        if threshold < 0 or threshold > 1:
            raise ValueError("The threshold must be between 0 and 1")
        if min_chars < 0:
            raise ValueError(
                "The minmum number of characters can't be negative."
            )
        criterion, __ = MinCharsCriterionRules.objects.get_or_create(
            threshold=threshold, min_chars=min_chars
        )
        return criterion
