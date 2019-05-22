# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from django.core.validators import MinValueValidator
from django.db import models

from reputation.logger import logger
from reputation.models.reputation_type import ReputationType

from ..criterion import Criterion


class NQuestionsCriterion(Criterion):
    name = models.CharField(
        max_length=32, default="n_questions", editable=False
    )
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

    def evaluate(self, teacher):
        super(NQuestionsCriterion, self).evaluate(teacher)
        if teacher.__class__.__name__ != "Teacher":
            msg = "`teacher` has to be of type Teacher."
            logger.error("TypeError: {}".format(msg))
            raise TypeError(msg)

        n_questions = teacher.user.question_set.count()

        if n_questions <= self.floor:
            return 0

        elif self.ceiling and n_questions >= self.ceiling:
            return 1

        else:
            if self.ceiling:
                n_questions = self.ceiling - n_questions
            return (
                1.0 / (1.0 + math.exp(-self.growth_rate * n_questions)) - 0.5
            ) * 2

    @staticmethod
    def info():
        return {
            "name": "n_questions",
            "full_name": "Number of questions",
            "description": "Gives a score between 0 and 100 representing the "
            "number of questions written by a teacher.",
        }

    @staticmethod
    def create_default():
        criterion = NQuestionsCriterion.objects.create()
        criterion.for_reputation_types.add(
            ReputationType.objects.get(type="teacher")
        )
        criterion.save()
        return criterion
