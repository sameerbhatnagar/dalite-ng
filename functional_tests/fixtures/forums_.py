import factory
import pytest

from pinax.forums.models import Forum


class ForumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Forum

    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence", nb_words=8)


@pytest.fixture
def forum():
    return ForumFactory()
