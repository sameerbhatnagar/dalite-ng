from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import (
    Quality,
    QualityType,
    QualityUseType,
    UsesCriterion,
    criterion,
)


@receiver(post_migrate)
def add_quality_types(sender, **kwargs):
    for quality_type in ("assignment", "group", "teacher", "global"):
        QualityType.objects.get_or_create(type=quality_type)


@receiver(post_migrate)
def add_quality_use_types(sender, **kwargs):
    for quality_use_type in ("validation", "evaluation"):
        QualityUseType.objects.get_or_create(type=quality_use_type)


@receiver(post_migrate)
def add_default_qualities(sender, **kwargs):

    if not criterion.MinWordsCriterion.objects.exists():
        criterion_ = criterion.MinWordsCriterion.objects.create(
            uses_rules="min_words"
        )
        criterion_.for_quality_types.add(
            QualityType.objects.get(type="assignment"),
            QualityType.objects.get(type="group"),
            QualityType.objects.get(type="teacher"),
            QualityType.objects.get(type="global"),
        )
        criterion_.save()
    if not criterion.MinWordsCriterionRules.objects.exists():
        criterion.MinWordsCriterionRules.get_or_create(
            threshold=1, min_words=4
        )

    if not Quality.objects.filter(quality_type__type="global").exists():
        quality = Quality.objects.create(
            quality_type=QualityType.objects.get(type="global"),
            quality_use_type=QualityUseType.objects.get(type="validation"),
        )
        UsesCriterion.objects.create(
            quality=quality, name="min_words", version=1, rules=1, weight=1
        )
