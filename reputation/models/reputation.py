# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models

from ..logger import logger
from .reputation_type import ReputationType


class Reputation(models.Model):
    reputation_type = models.ForeignKey(ReputationType)

    def __str__(self):
        return "{} for {}: {}".format(
            self.pk, self.reputation_type, self.reputation_model
        )

    def evaluate(self):
        """
        Returns the reputation of the linked model as a tuple of the quality
        and the different criterion results.

        Returns
        -------
        Optional[float]
            Quality of the answer or None of no criterions present
        List[Dict[str, Any]]
            Individual criterions under the format
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
        ValueError
            If this reputation doesn't correspond to any type of reputation
        """
        return self.reputation_type.evaluate(self.reputation_model)

    @property
    def reputation_model(self):
        """
        Returns the model corresponding to this instance.

        Returns
        -------
        Model
            Model instance

        Raises
        ------
        ValueError
            If this reputation doesn't correspond to any type of reputation
        """
        for model in ReputationType.objects.values_list("type", flat=True):
            if hasattr(self, model):
                return getattr(self, model)
        msg = (
            "Reputation needs to have a OneToOne field with a model defined "
            "as a ReputationType. See Teacher for an example."
        )
        logger.error(msg)
        raise ValueError(msg)

    @staticmethod
    def create(cls):
        """
        Creates an instance of Reputation.

        Parameters
        ----------
        cls : Union[str, object]
            Model class for which to create the instance. Converted to string
            if object passed

        Returns
        -------
        Reputation
            Created instance

        Raises
        ------
        TypeError
            If the `cls` isn't a string
        ReputationType.DoesNotExist
            If there is no reputation type for the given class
        """
        if not isinstance(cls, basestring):
            cls = cls.__class__.__name__

        reputation_type = ReputationType.objects.get(type=cls.lower())

        return Reputation.objects.create(reputation_type=reputation_type)


class ReputationHistory(models.Model):
    reputation = models.ForeignKey(Reputation, editable=False)
    datetime = models.DateTimeField(auto_now_add=True)
    reputation_value = models.FloatField(null=True, blank=True, editable=False)
    reputation_details = models.TextField(editable=False)

    @staticmethod
    def create(reputation):
        value, details = reputation.evaluate()
        return ReputationHistory.objects.create(
            reputation=reputation,
            reputation_value=value,
            reputation_details=json.dumps(details),
        )
