from quality.models import (
    MinWordsCriterion,
    MinWordsCriterionRules,
    Quality,
    QualityType,
    UsesCriterion,
)


def test_quality_types_exist():
    for type_ in ("assignment", "group", "teacher", "global"):
        assert QualityType.objects.filter(type=type_).exists()


def test_default_quality():
    assert Quality.objects.filter(quality_type__type="global").exists()
    assert MinWordsCriterion.objects.exists()
    assert MinWordsCriterionRules.objects.exists()
    assert UsesCriterion.objects.filter(
        quality=Quality.objects.get(quality_type__type="global")
    ).exists()
