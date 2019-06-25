# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django.core.exceptions import ValidationError
from django.db import models

from dalite.models.custom_fields import CommaSepField
from reputation.logger import logger

from ..reputation_type import ReputationType


def validate_list_floats_greater_0(val):
    for x in val:
        try:
            n = float(x)
        except ValueError:
            raise ValidationError(
                "The values must be comma separated floats greather or equal "
                "to 0."
            )
        if n < 0:
            raise ValidationError(
                "The values must be comma separated floats greather or equal "
                "to 0."
            )


class Criterion(models.Model):
    version = models.AutoField(primary_key=True)
    for_reputation_types = models.ManyToManyField(ReputationType)
    badge_thresholds = CommaSepField(
        distinct=True,
        blank=True,
        validators=[validate_list_floats_greater_0],
        help_text="Thresholds for the badges to be awarded.",
    )

    class Meta:
        abstract = True

    def __iter__(self):
        """
        Any attribute specific to the criterion version  should
        be added in the __iter__ method of the child model.
        You can use
        return itertools.chain(`child_iter`, Super(`Class`, self).__iter__())`
        to combine them.
        """
        return chain(
            self.__class__.info().iteritems(),
            {
                "version": self.version,
                "badge_thresholds": self.badge_thresholds,
            }.iteritems(),
        )

    def __str__(self):
        return "{}: version {}".format(self.name, self.version)

    def evaluate(self, model):
        """
        Evaluates the reputation score of the given `model`. Classes inheriting
        must call the super method.

        Parameters
        ----------
        model : Model
            Model being evaluated. Must be in `for_reputation_types`

        Returns
        -------
        float in [0,1]
            Reputation as evaluated by the criterion

        Raises
        ------
        TypeError
            If the `model` isn't in the for_reputation_types
        """
        if not self.for_reputation_types.filter(
            type=model.__class__.__name__.lower()
        ):
            msg = "The criterion {} isn't available ".format(
                str(self)
            ) + "for reputation type {}.".format(
                model.__class__.__name__.lower()
            )
            logger.error(msg)
            raise TypeError(msg)

    def save(self, *args, **kwargs):
        """
        Saves the new criterion making sure the `name` field exists.
        """
        if not hasattr(self, "name"):
            raise NotImplementedError(
                "Your criterion needs to have a `name` field. Make sure it's "
                "different from the others or it may lead to some trouble "
                "down the line."
            )
        super(Criterion, self).save(*args, **kwargs)

    @staticmethod
    def info():
        raise NotImplementedError("This method has to be implemented.")
