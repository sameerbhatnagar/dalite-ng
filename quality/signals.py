from operator import itemgetter

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Quality, QualityType, QualityUseType
from .models.criterion.criterion_list import criterions


@receiver(post_migrate)
def add_quality_types(sender, **kwargs):
    types = (
        ("assignment", "studentgroupassignment"),
        ("group", "studentgroup"),
        ("teacher", "teacher"),
        ("global", None),
    )
    for quality_type, type_model in types:
        try:
            type_ = QualityType.objects.get(type=quality_type)
            if type_.model is None:
                type_.model = type_model
                type_.save()
        except QualityType.DoesNotExist:
            type_ = QualityType.objects.create(
                type=quality_type, model=type_model
            )


@receiver(post_migrate)
def add_quality_use_types(sender, **kwargs):
    for quality_use_type in ("validation", "evaluation"):
        QualityUseType.objects.get_or_create(type=quality_use_type)


@receiver(post_migrate)
def add_default_qualities(sender, **kwargs):

    for criterion in map(itemgetter("criterion"), criterions.values()):
        if not criterion.objects.exists():
            criterion.create_default()

    for use_type in ("validation", "evaluation"):
        if not Quality.objects.filter(
            quality_type__type="global", quality_use_type__type=use_type
        ).exists():
            quality = Quality.objects.create(
                quality_type=QualityType.objects.get(type="global"),
                quality_use_type=QualityUseType.objects.get(type=use_type),
            )
