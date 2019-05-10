# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from reputation.logger import logger


class ReputationType(models.Model):
    type = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.type

    def evaluate(self, model):
        """
        Returns the reputation of the linked model as a tuple of the quality
        and the different criterion results.

        Parameters
        ----------
        model : Union[Question, Assignment, Teacher]
            Model for which to evaluate the reputation

        Returns
        -------
        Optional[float]
            Quality of the answer or None of no criterions present
        List[Dict[str, Any]]
            Individual criterions under the format
                [{
                    name: str
                    version: int
                    weight: int
                    value: float
                }]

        Raises
        ------
        TypeError
            If the given `model` doesn't correspond to the `type`
        """
        if model.__class__.lower() != self.type:
            msg = (
                "The type of `model` doesn't correspond to the correct "
                "type; is {} instead of {}.".format(
                    model.__class__.lower(), self.type
                )
            )
            logger.error("TypeError: {}".format(msg))
            raise TypeError(msg)


class UsesCriterion(models.Model):
    reputation_type = models.ForeignKey(
        ReputationType, related_name="criterions"
    )
