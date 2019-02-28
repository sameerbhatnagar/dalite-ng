import pytest
from django.db import models

from quality.models import Criterion


def test_doesn_t_implement_evaluate():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    criterion = FakeCriterion.objects.create()
    with pytest.raises(NotImplementedError):
        criterion.evaluate(None)
