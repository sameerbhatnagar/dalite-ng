import pytest

from quality.models import Quality, QualityType, QualityUseType


@pytest.fixture
def global_validation_quality():
    return Quality.objects.get(
        quality_type__type="global", quality_use_type__type="validation"
    )


@pytest.fixture
def validation_quality_use_type():
    return QualityUseType.objects.get(type="validation")


@pytest.fixture
def assignment_quality_type():
    return QualityType.objects.get(type="assignment")


@pytest.fixture
def assignment_validation_quality(
    assignment_quality_type, validation_quality_use_type
):
    return Quality.objects.create(
        quality_type=assignment_quality_type,
        quality_use_type=validation_quality_use_type,
    )


@pytest.fixture
def assignment_validation_qualities(
    assignment_quality_type, validation_quality_use_type
):
    return [
        Quality.objects.create(
            quality_type=assignment_quality_type,
            quality_use_type=validation_quality_use_type,
        ),
        Quality.objects.create(
            quality_type=assignment_quality_type,
            quality_use_type=validation_quality_use_type,
        ),
    ]
