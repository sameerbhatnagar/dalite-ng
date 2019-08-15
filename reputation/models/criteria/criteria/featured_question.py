# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from reputation.logger import logger

from ..criterion import Criterion


class FeaturedQuestionCriterion(Criterion):
    name = models.CharField(
        max_length=32, default="featured_question", editable=False
    )

    def evaluate(self, instance):
        """
        Evaluate a question based on:
            - how many student answers it has, weighted by what fraction
            of students switched answers


        Parameters
        ----------
        instance : question
            question object

        Returns
        -------
        float
            Reputation as evaluated by the criterion

        Raises
        ------
        TypeError
            If `instance` isn't of type Question
        """
        super(FeaturedQuestionCriterion, self).evaluate(instance)
        if instance.__class__.__name__ == "Question":
            result = 1.0
            return (result, {})
        else:
            msg = "`instance` has to be of type Question."
            logger.error("TypeError: {}".format(msg))
            raise TypeError(msg)

    def info(self):
        return super(FeaturedQuestionCriterion, self).info(
            {
                "name": "featured_question",
                "full_name": "Featured Question",
                "description": "Questions that have produced student answers "
                "that get others to change their mind.",
            }
        )
