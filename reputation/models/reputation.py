# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .reputation_type import ReputationType


class Reputation(models.Model):
    reputation_type = models.ForeignKey(ReputationType)

    def __str__(self):
        return "{} for {}: {}".format(
            self.pk,
            self.reputation_type,
            str(
                getattr(self, "{}_set".format(self.quality_type.type)).first()
            ),
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
                    version: int
                    weight: int
                    value: float
                }]

        Raises
        ------
        AttributeError
            If the OneToOne field wasn't correctly set with the `related_name`
            as "reputation_model"
        """
        try:
            return self.reputation_type.evaluate(self.reputation_model)
        except AttributeError:
            raise AttributeError(
                "The OneToOne field to Reputation needs to have as "
                '`related_name` "reputation_model".'
            )

    @staticmethod
    def create(cls):
        """
        Creates an instance of Reputation.

        Parameters
        ----------
        cls : str
            Model class for which to create the instance

        Returns
        -------
        Reputation
            Created instance

        Raises
        ------
        ReputationType.DoesNotExist
            If there is no reputation type for the given class
        """
        if not isinstance(cls, basestring):
            raise TypeError("`cls` must be of type `str`.")

        reputation_type = ReputationType.objects.get(type=cls.lower())

        return Reputation.objects.create(reputation_type=reputation_type)
