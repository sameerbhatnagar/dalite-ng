from quality.models import Quality, QualityType, UsesCriterion


def test_default_quality():
    assert Quality.objects.exists()
    assert UsesCriterion.objects.exists()


def test_quality_types_exist():
    for type_ in ("assignment", "group", "teacher"):
        assert QualityType.objects.filter(type=type_).exists()
