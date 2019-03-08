import mock

from quality.models import UsesCriterion
from quality.tests.fixtures import *  # noqa


def test_dict(assignment_quality):
    with mock.patch(
        "quality.models.quality.get_criterion"
    ) as get_criterion, mock.patch("quality.models.quality.models.Model.save"):
        rules = mock.MagicMock()
        del rules.keys
        rules.__iter__.return_value = {"a": 1, "b": 2, "c": 3}.items()

        criterion_ = mock.MagicMock()
        del criterion_.keys
        criterion_.__iter__.return_value = {
            "version": 0,
            "is_beta": False,
        }.items()
        criterion_.rules = ["a", "b", "c"]

        criterion_class = mock.Mock()
        criterion_class.objects.get.return_value = criterion_
        criterion_class.objects.count.return_value = 1

        criterion_rules_class = mock.Mock()
        criterion_rules_class.objects.get.return_value = rules

        get_criterion.return_value = {
            "criterion": criterion_class,
            "rules": criterion_rules_class,
        }

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
        assert "version" in data
        assert "is_beta" in data
        assert len(data) == 6


def test_dict__subset_of_rules(assignment_quality):
    with mock.patch(
        "quality.models.quality.get_criterion"
    ) as get_criterion, mock.patch("quality.models.quality.models.Model.save"):
        rules = mock.MagicMock()
        del rules.keys
        rules.__iter__.return_value = {"a": 1, "b": 2, "c": 3}.items()

        criterion_ = mock.MagicMock()
        del criterion_.keys
        criterion_.__iter__.return_value = {
            "version": 0,
            "is_beta": False,
        }.items()
        criterion_.rules = ["a", "c"]

        criterion_class = mock.Mock()
        criterion_class.objects.get.return_value = criterion_
        criterion_class.objects.count.return_value = 1

        criterion_rules_class = mock.Mock()
        criterion_rules_class.objects.get.return_value = rules

        get_criterion.return_value = {
            "criterion": criterion_class,
            "rules": criterion_rules_class,
        }

        criterion = UsesCriterion.objects.create(
            quality=assignment_quality,
            name="fake",
            version=0,
            rules=0,
            weight=1,
        )
        data = dict(criterion)
        assert data["a"] == 1
        assert "b" not in data
        assert data["c"] == 3
        assert data["weight"] == 1
        assert "version" in data
        assert "is_beta" in data
        assert len(data) == 5
