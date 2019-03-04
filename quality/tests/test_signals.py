from quality.models import Quality, UsesCriterion


def test_default_quality():
    assert Quality.objects.exists()
    assert UsesCriterion.objects.exists()
