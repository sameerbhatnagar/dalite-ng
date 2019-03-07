from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Quality, QualityType, UsesCriterion, criterion


@receiver(post_migrate)
def add_quality_types(sender, **kwargs):
    for quality_type in ("assignment", "group", "teacher"):
        QualityType.objects.get_or_create(type=quality_type)


@receiver(post_migrate)
def add_default_qualities(sender, **kwargs):
    for quality_type in QualityType.objects.all():
        if not Quality.objects.filter(quality_type=quality_type).exists():
            if not criterion.MinWordsCriterion.objects.exists():
                criterion_ = criterion.MinWordsCriterion.objects.create(
                    uses_rules="min_words"
                )
                criterion_.for_quality_types.add(
                    QualityType.objects.get(type="assignment"),
                    QualityType.objects.get(type="group"),
                    QualityType.objects.get(type="teacher"),
                )
                criterion_.save()
            if not criterion.MinWordsCriterionRules.objects.exists():
                criterion.MinWordsCriterionRules.get_or_create(min_words=4)

            quality = Quality.objects.create(quality_type=quality_type)
            UsesCriterion.objects.create(
                quality=quality, name="min_words", version=0, rules=0, weight=1
            )
