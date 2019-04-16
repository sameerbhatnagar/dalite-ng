from quality.models import (
    MinCharsCriterion,
    MinWordsCriterion,
    NegWordsCriterion,
    Quality,
    QualityType,
    QualityUseType,
)


def test_quality_types_exist():
    for type_ in (
        "studentgroupassignment",
        "studentgroup",
        "teacher",
        "global",
    ):
        assert QualityType.objects.filter(type=type_).exists()


def test_quality_use_types_exist():
    for type_ in ("validation", "evaluation"):
        assert QualityUseType.objects.filter(type=type_).exists()


def test_default_quality():
    assert Quality.objects.filter(
        quality_type__type="global", quality_use_type__type="validation"
    ).exists()
    assert Quality.objects.filter(
        quality_type__type="global", quality_use_type__type="evaluation"
    ).exists()
    assert MinWordsCriterion.objects.exists()
    assert MinCharsCriterion.objects.exists()
    assert NegWordsCriterion.objects.exists()
