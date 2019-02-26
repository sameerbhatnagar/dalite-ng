# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models

from peerinst.models import Answer

from .criterion.criterion_list import criterions

logger = logging.getLogger("quality")


class UsesCriterion(models.Model):
    name = models.CharField(max_length=32)
    version = models.PositiveIntegerField()
    use_latest = models.BooleanField()
    weigth = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        """
        Saves the new criterion making sure only one exists for each criterion
        name.
        """
        try:
            criterion = criterions[self.name]
        except KeyError:
            logger.error("There is no criterion named %s.", self.name)
            raise ValueError(
                "The used criterion has an invalid name or version."
            )
        if self.version >= criterion.objects.all().count():
            logger.error(
                "The criterion %s doesn't have a version %d.",
                self.name,
                self.version,
            )
            raise ValueError(
                "The used criterion has an invalid name or version."
            )
        UsesCriterion.objects.filter(name=self.name).delete()
        super(UsesCriterion, self).save(*args, **kwargs)


class Quality(models.Model):
    criterions = models.ManyToManyField(UsesCriterion)


class AnswerQuality(models.Model):
    quality_model = models.ForeignKey(Quality)
    answer = models.ForeignKey(Answer)

    @property
    def quality(self):
        """
        Quality as a weigthed mean of the different criterions.

        Returns
        -------
        float
            Quality
        """
        return self.broken_down_quality[0]

    @property
    def broken_down_quality(self):
        """
        Quality as a tuple of the quality and the different criterion results.

        Returns
        -------
        float
            Quality of the answer
        List[Dict[str, Any]]
            Individual criterions under the format
                [{
                    name: str
                    version: int
                    weight: int
                    quality: float
                }]
        """
        qualities = [
            {
                "name": criterion.criterion.name,
                "version": criterion.criterion.version,
                "weight": criterion.weight,
                "quality": criterion.criterion.evaluate(self.answer),
            }
            for criterion in self.quality_model.usescriterion_set.all()
        ]
        quality = sum(q["quality"] * q["weight"] for q in qualities) / sum(
            q["weight"] for q in qualities
        )
        return quality, qualities
