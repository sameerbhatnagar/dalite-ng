import pytest

from quality.models import Quality, QualityType


@pytest.fixture
def assignment_quality_type():
    return QualityType.objects.get(type="assignment")


@pytest.fixture
def assignment_quality(assignment_quality_type):
    return Quality.objects.create(quality_type=assignment_quality_type)


@pytest.fixture
def assignment_qualities(assignment_quality_type):
    return [
        Quality.objects.create(quality_type=assignment_quality_type),
        Quality.objects.create(quality_type=assignment_quality_type),
    ]
