# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models

from .criterion.criterion_list import criterions, get_criterion
from .quality_type import QualityType

logger = logging.getLogger("quality")


class Quality(models.Model):
    quality_type = models.ForeignKey(QualityType)

    def evaluate(self, answer, *args, **kwargs):
        """
        Returns the quality as a tuple of the quality and the different
        criterion results.

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
                    quality: float
                }]
        """
        if not self.criterions.exists():
            return None, []

        criterions_ = [
            {
                "criterion": (
                    get_criterion(c.name)["criterion"].objects.get(
                        version=c.version
                    )
                ),
                "weight": c.weight,
            }
            for c in self.criterions.all()
        ]
        qualities = [
            {
                "name": c["criterion"].name,
                "version": c["criterion"].version,
                "weight": c["weight"],
                "quality": c["criterion"].evaluate(
                    answer, c["criterion"].rules, *args, **kwargs
                ),
            }
            for c in criterions_
        ]
        quality = float(
            sum(q["quality"] * q["weight"] for q in qualities)
        ) / sum(q["weight"] for q in qualities)
        return quality, qualities

    def add_criterion(self, name):
        if name not in [c.name for c in self.available]:
            msg = "The criterion {} isn't available for quality {}.".format(
                name, self.pk
            )
            logger.error(msg)
            raise ValueError(msg)

        criterion_class = get_criterion(name)

        rules = criterion_class["rules"].get_or_create()

        UsesCriterion.objects.create(
            quality=self,
            name=name,
            version=criterion_class["criterion"]
            .objects.filter(for_quality_types=self.quality_type)
            .last(),
            rules=rules.pk,
            weight=1,
        )

    @property
    def available(self):
        return [
            criterion
            for criterion in criterions.values()
            if criterion.objects.filter(
                for_quality_types=self.quality_type
            ).exists()
        ]

    @property
    def available_info(self):
        return [criterion.info() for criterion in self.available]


class UsesCriterion(models.Model):
    quality = models.ForeignKey(Quality, related_name="criterions")
    name = models.CharField(max_length=32)
    version = models.PositiveIntegerField()
    rules = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()

    def __iter__(self):
        criterion_class = get_criterion(self.name)
        criterion = criterion_class["criterion"].objects.get(
            version=self.version
        )
        rules = criterion_class["rules"].objects.get(pk=self.rules)
        data = dict(criterion)
        data.update(
            {
                key: value
                for key, value in dict(rules).items()
                if key in criterion.rules
            }
        )
        data.update({"weight": self.weight})
        return ((field, value) for field, value in data.items())
