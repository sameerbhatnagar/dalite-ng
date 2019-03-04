from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Quality, UsesCriterion, criterion


@receiver(post_migrate)
def add_default_quality_signal(sender, **kwargs):

    if not Quality.objects.exists():
        try:
            min_words_criterion = criterion.MinWordsCriterion.create(
                min_words=4
            )
        except criterion.CriterionExistsError:
            pass
        quality = Quality.objects.create()
        UsesCriterion.objects.create(
            quality=quality,
            name="min_words",
            version=0,
            use_latest=True,
            weight=1,
        )
