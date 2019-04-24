from operator import itemgetter

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import LikelihoodLanguage, Quality, QualityType, QualityUseType
from .models.criterion.criterion_list import criterions


@receiver(post_migrate)
def add_quality_types(sender, **kwargs):
    for quality_type in (
        "studentgroupassignment",
        "studentgroup",
        "teacher",
        "global",
    ):
        QualityType.objects.get_or_create(type=quality_type)


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


@receiver(post_migrate)
def add_likelihood_languages(sender, **kwargs):
    languages = [
        {
            "language": "english",
            "left_to_right": True,
            "n_gram_urls": [
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "english_monograms.txt",
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "english_bigrams_1.txt",
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "english_trigrams.txt.zip",
            ],
        },
        {
            "language": "french",
            "left_to_right": True,
            "n_gram_urls": [
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "french_monograms.txt",
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "french_bigrams_1.txt",
                "http://practicalcryptography.com/media/cryptanalysis/files/"
                "french_trigrams.txt.zip",
            ],
        },
    ]

    for language in languages:
        if not LikelihoodLanguage.objects.filter(
            language=language["language"]
        ).exists():
            LikelihoodLanguage.objects.create(**language)
