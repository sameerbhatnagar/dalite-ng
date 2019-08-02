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

    def _calculate_points(self, criterion, model):
        """
        Calculates the number of points returned by the model based on the
        criterion evaluation and its point thresholds.

        Parameters
        ----------
        criterion : Criterion
            Criterion used for the evaluation
        model : Union[Question, Assignment, Teacher]
            Model for which to evaluate the reputation

        Returns
        -------
        float
            Reputation as evaluated by the criterion

        Raises
        ------
        TypeError
            If the given `model` doesn't correspond to the `type`
        """
        evaluation = criterion.evaluate(model)

        if criterion.thresholds:
            points = sum(
                float(points_)
                * (min(evaluation, float(threshold)) - float(prev_threshold))
                for points_, threshold, prev_threshold in zip(
                    criterion.points_per_threshold,
                    criterion.thresholds,
                    [0] + criterion.thresholds[:-1],
                )
            )
            if len(criterion.points_per_threshold) > len(criterion.thresholds):
                points = points + float(criterion.points_per_threshold[-1]) * (
                    evaluation - float(criterion.thresholds[-1])
                )

        else:
            points = criterion.points_per_threshold[0] * evaluation

        print("TEST")
        print(evaluation)
        print(points)

        return points

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
            Quality of the answer or None of no criteria present
        List[Dict[str, Any]]
            Individual criteria under the format
                [{
                    name: str
                    full_name: str
                    description: str
                    version: int
                    weight: int
                    reputation: float
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

        if not self.criteria.exists():
            return None, []

        reputations = [
            dict(
                chain(
                    {
                        "reputation": self._calculate_points(criterion, model)
                    }.items(),
                    criterion.__iter__(),
                )
            )
            for criterion in (
                get_criterion(c.name).objects.get(version=c.version)
                for c in self.criteria.all()
            )
        ]
        print(reputations)
        reputation = sum(r["reputation"] for r in reputations)

        return reputation, reputations


class UsesCriterion(models.Model):
    reputation_type = models.ForeignKey(
        ReputationType, related_name="criteria"
    )
    name = models.CharField(max_length=32)
    version = models.PositiveIntegerField()

    def __iter__(self):
        criterion_class = get_criterion(self.name)
        criterion = criterion_class.objects.get(version=self.version)
        return iter(criterion)

    def __str__(self):
        return "{} for reputation type {}".format(
            self.name, str(self.reputation_type)
        )
