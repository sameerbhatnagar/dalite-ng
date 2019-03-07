import mock
import pytest

from quality.models import UsesCriterion
from quality.tests.fixtures import *  # noqa


def test_save(assignment_quality):
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 1
        get_criterion.return_value = criterion

        UsesCriterion.objects.create(
            quality=assignment_quality,
            name="test",
            version=0,
            rules=0,
            weight=1,
        )

        assert UsesCriterion.objects.filter(
            quality=assignment_quality, name="test", version=0
        ).exists()


def test_save__invalid_version(assignment_quality):
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 1
        get_criterion.return_value = criterion

        with pytest.raises(ValueError):
            UsesCriterion.objects.create(
                quality=assignment_quality,
                name="test",
                version=1,
                rules=0,
                weight=1,
            )


def test_save__previous_version_removed(assignment_qualities):
    quality_1 = assignment_qualities[0]
    quality_2 = assignment_qualities[1]
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion = mock.Mock()
        criterion.objects.count.return_value = 2
        get_criterion.return_value = criterion

        UsesCriterion.objects.create(
            quality=quality_1, name="test", version=0, rules=0, weight=1
        )
        UsesCriterion.objects.create(
            quality=quality_2, name="test", version=0, rules=0, weight=1
        )

        assert UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=0, rules=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_2, name="test", version=0, rules=0
        ).exists()

        UsesCriterion.objects.create(
            quality=quality_1, name="test", version=1, rules=0, weight=1
        )

        assert not UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=0, rules=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=1, rules=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_2, name="test", version=0, rules=0
        ).exists()

        UsesCriterion.objects.create(
            quality=quality_1, name="test", version=1, rules=1, weight=1
        )

        assert not UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=1, rules=0
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_1, name="test", version=1, rules=1
        ).exists()
        assert UsesCriterion.objects.filter(
            quality=quality_2, name="test", version=0, rules=0
        ).exists()


def test_dict(assignment_quality):
    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion_ = mock.Mock()
        criterion_.serialize.return_value = {"a": 1, "b": 2, "c": 3}
        criterion_class = mock.Mock()
        get_criterion.return_value = criterion_class
        criterion_class.objects.get.return_value = criterion_
        criterion_class.objects.count.return_value = 1

        criterion = UsesCriterion.objects.create(
            quality=assignment_quality,
            name="fake",
            version=0,
            rules=0,
            weight=1,
        )
        data = dict(criterion)
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 3
        assert data["weight"] == 1
