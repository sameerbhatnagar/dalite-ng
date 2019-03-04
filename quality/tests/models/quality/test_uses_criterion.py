import mock
import pytest

from quality.models import Quality, UsesCriterion


def test_save():
    quality = Quality.objects.create()
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 1
        get_criterion.return_value = criterion

        UsesCriterion.objects.create(
            quality=quality, name="test", version=0, use_latest=True, weight=1
        )

        assert UsesCriterion.objects.filter(
            quality=quality, name="test", version=0
        ).exists()


def test_save__invalid_version():
    quality = Quality.objects.create()
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 1
        get_criterion.return_value = criterion

        with pytest.raises(ValueError):
            UsesCriterion.objects.create(
                quality=quality,
                name="test",
                version=1,
                use_latest=True,
                weight=1,
            )


def test_save__previous_version_removed():
    quality_1 = Quality.objects.create()
    quality_2 = Quality.objects.create()
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 2
        get_criterion.return_value = criterion

        UsesCriterion.objects.create(
            quality=quality_1,
            name="test",
            version=0,
            use_latest=True,
            weight=1,
        )
        UsesCriterion.objects.create(
            quality=quality_2,
            name="test",
            version=0,
            use_latest=True,
            weight=1,
        )

        assert UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_2, name="test", version=0
        ).exists()

        UsesCriterion.objects.create(
            quality=quality_1,
            name="test",
            version=1,
            use_latest=True,
            weight=1,
        )

        assert not UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=1
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_2, name="test", version=0
        ).exists()
