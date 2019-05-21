# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django.db import models

from criterion_list import get_criterion

from ..logger import logger


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
        if model.__class__.__name__.lower() != self.type:
            msg = (
                "The type of `model` doesn't correspond to the correct "
                "type; is {} instead of {}.".format(
                    model.__class__.__name__.lower(), self.type
                )
            )
            logger.error("TypeError: {}".format(msg))
            raise TypeError(msg)

        if not self.criterions.exists():
            return None, []

        criterions = [
            {
                "criterion": get_criterion(c.name).objects.get(
                    version=c.version
                ),
                "weight": c.weight,
            }
            for c in self.criterions.all()
        ]

        reputations = [
            dict(
                chain(
                    {
                        "reputation": c["criterion"].evaluate(model),
                        "weight": c["weight"],
                    }.items(),
                    c["criterion"].__iter__(),
                )
            )
            for c in criterions
        ]

        reputation = float(
            sum(r["reputation"] * r["weight"] for r in reputations)
        ) / float(sum(r["weight"] for r in reputations))

        return reputation, reputations


class UsesCriterion(models.Model):
    reputation_type = models.ForeignKey(
        ReputationType, related_name="criterions"
    )
    name = models.CharField(max_length=32)
    version = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    def __iter__(self):
        criterion_class = get_criterion(self.name)
        criterion = criterion_class.objects.get(version=self.version)
        data = dict(criterion)
        data.update({"weight": self.weight})
        return ((field, value) for field, value in data.items())

    def __str__(self):
        return "{} for reputation type {}".format(
            self.name, str(self.reputation_type)
        )
