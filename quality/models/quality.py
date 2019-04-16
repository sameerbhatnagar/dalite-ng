# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from itertools import chain

from django.contrib.contenttypes.models import ContentType
from django.db import models

from .criterion.criterion_list import criterions, get_criterion
from .quality_type import QualityType, QualityUseType

logger = logging.getLogger("quality")


class Quality(models.Model):
    quality_type = models.ForeignKey(QualityType)
    quality_use_type = models.ForeignKey(QualityUseType)

    def __str__(self):
        if self.quality_type.type == "global":
            return "{} for {} and use type {}".format(
                self.pk, self.quality_type, self.quality_use_type
            )
        else:
            contenttype = ContentType.objects.get(
                app_label="peerinst", model=self.quality_type.type
            )
            for_ = str(
                contenttype.model_class().objects.filter(quality=self).first()
            )

            return "{} for {}: {} and use type {}".format(
                self.pk, self.quality_type, for_, self.quality_use_type
            )

    def __iter__(self):
        return chain(
            {
                "pk": self.pk,
                "quality_type": self.quality_type.type,
                "quality_use_type": self.quality_use_type.type,
            }.iteritems(),
            *(
                dict(criterion).iteritems()
                for criterion in self.criterions.all()
            )
        )

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
                    threshold: float
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
                "rules": c.rules,
                "weight": c.weight,
            }
            for c in self.criterions.all()
        ]
        qualities = [
            dict(
                chain(
                    dict(c["criterion"]).iteritems(),
                    {
                        "weight": c["weight"],
                        "quality": c["criterion"].evaluate(
                            answer, c["rules"], *args, **kwargs
                        ),
                    }.iteritems(),
                )
            )
            for c in criterions_
        ]
        quality = float(
            sum(q["quality"]["quality"] * q["weight"] for q in qualities)
        ) / sum(q["weight"] for q in qualities)
        return quality, qualities

    def add_criterion(self, name):
        """
        Adds the given criterion with latest version and default rules to the
        quality.

        Parameters
        ----------
        name : str
            Name of the criterion

        Returns
        -------
        UsesCriterion
            Created criterion

        Raises
        ------
        ValueError
            If the given criterion doesn't exist or isn't available for this
            quality type
        """
        if name not in [c["name"] for c in self.available]:
            msg = "The criterion {} isn't available for quality {}.".format(
                name, self.pk
            )
            logger.error(msg)
            raise ValueError(msg)

        criterion_class = get_criterion(name)

        version = (
            criterion_class["criterion"]
            .objects.filter(for_quality_types=self.quality_type)
            .last()
            .version
        )

        rules = criterion_class["rules"].get_or_create()

        return UsesCriterion.objects.create(
            quality=self, name=name, version=version, rules=rules.pk, weight=1
        )

    def update_criterion(self, name, field, value):
        """
        Modifies the given criterion field with value.

        Parameters
        ----------
        name : str
            Name of the criterion
        field : str
            Field to modify
        value : Any
            New value

        Returns
        -------
        UsesCriterion
            Updated criterion
        Any
            Previous value of the field

        Raises
        ------
        AttributeError
            If the given field doesn't exist
        UsesCriterion.DoesNotExist
            If there is no used criterio with the given name
        """
        try:
            criterion = UsesCriterion.objects.get(quality=self, name=name)
        except UsesCriterion.DoesNotExist:
            raise UsesCriterion.DoesNotExist(
                "There is no criterion with name {}.".format(name)
            )

        if field in ("version", "weight"):
            old_value = getattr(criterion, field)
            setattr(criterion, field, value)
            criterion.save()
        else:
            rules = get_criterion(name)["rules"].objects.get(
                pk=criterion.rules
            )
            old_value = getattr(rules, field)
            type_ = dict(rules)[field]["type"]
            if type_ == "CommaSepField":
                if value:
                    value = old_value + [value]
                else:
                    value = old_value[:-1]
            setattr(rules, field, value)
            rules.save()

        return criterion, old_value, value

    def remove_criterion(self, name):
        UsesCriterion.objects.filter(quality=self, name=name).delete()

    @property
    def available(self):
        return [
            criterion["criterion"].info()
            for criterion in criterions.values()
            if criterion["criterion"]
            .objects.filter(for_quality_types=self.quality_type)
            .exists()
        ]


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
                if key in criterion.rules or key == "threshold"
            }
        )
        data.update({"weight": self.weight, "id": self.pk})
        return ((field, value) for field, value in data.items())

    def __str__(self):
        return "{} for quality {}".format(self.name, str(self.quality))
