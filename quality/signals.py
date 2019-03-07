from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Quality, UsesCriterion, criterion


@receiver(post_migrate)
def add_default_quality_signal(sender, **kwargs):

    if not Quality.objects.exists():
        if not criterion.MinWordsCriterion.objects.exists():
            criterion.MinWordsCriterion.objects.create(uses_rules="min_words")
        if not criterion.MinWordsCriterionRules.objects.exists():
            criterion.MinWordsCriterionRules.create(min_words=4)

        quality = Quality.objects.create()
        UsesCriterion.objects.create(
            quality=quality, name="min_words", version=0, rules=0, weight=1
        )
