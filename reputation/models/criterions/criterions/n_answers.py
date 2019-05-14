# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from django.core.validators import MinValueValidator
from django.db import models

from reputation.logger import logger
from reputation.models.reputation_type import ReputationType

from ..criterion import Criterion


class NAnswersCriterion(Criterion):
    name = models.CharField(max_length=32, default="n_answers", editable=False)
    floor = models.PositiveIntegerField(
        verbose_name="Number floor",
        default=0,
        help_text="Any number of answers up to and including this evaluates "
        "to 0.",
    )
    ceiling = models.PositiveIntegerField(
        verbose_name="Number ceiling",
        default=100,
        help_text="Any number of answers from and including this evaluates "
        "to 1. If set to 0, no ceiling is set.",
    )
    growth_rate = models.FloatField(
        default=0.01,
        help_text="Steepness of the slope.",
        validators=[MinValueValidator(0.0)],
    )

    def evaluate(self, question):
        super(NAnswersCriterion, self).evaluate(question)
        if not hasattr(question, "answer_set"):
            msg = "`question` has to be of type Question."
            logger.error("TypeError: {}".format(question))
            raise TypeError(msg)

        n_answers = question.answer_set.count()

        if n_answers <= self.floor:
            return 0

        elif self.ceiling and n_answers >= self.ceiling:
            return 1

        else:
            if self.ceiling:
                n_answers = self.ceiling - n_answers
            return (
                1.0 / (1.0 + math.exp(-self.growth_rate * n_answers)) - 0.5
            ) * 2

    @staticmethod
    def info():
        return {
            "name": "n_answers",
            "full_name": "Number of answers",
            "description": "Gives a score between 0 and 1 representing the "
            "number of answers for a question. Range is enforced by using "
            "the sigmoid function.",
        }

    @staticmethod
    def create_default():
        criterion = NAnswersCriterion.objects.create()
        criterion.for_reputation_types.add(
            ReputationType.objects.get(type="question")
        )
        criterion.save()
        return criterion
