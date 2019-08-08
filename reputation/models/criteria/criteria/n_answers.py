# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from reputation.logger import logger

from ..criterion import Criterion


class NAnswersCriterion(Criterion):
    name = models.CharField(max_length=32, default="n_answers", editable=False)

    def evaluate(self, question):
        """
        Evaluates the `questions` using the number of answers to it.

        Parameters
        ----------
        question : Question
            Question to evaluate

        Returns
        -------
        float
            Reputation as evaluated by the criterion

        Raises
        ------
        TypeError
            If `question` isn't of type Question
        """
        super(NAnswersCriterion, self).evaluate(question)
        if question.__class__.__name__ != "Question":
            msg = "`question` has to be of type Question."
            logger.error("TypeError: {}".format(msg))
            raise TypeError(msg)

        return question.answer_set.count()

    @staticmethod
    def info():
        return {
            "name": "n_answers",
            "full_name": "Number of answers",
            "description": "Gives a score between 0 and 100 representing the "
            "number of answers for a question.",
        }
