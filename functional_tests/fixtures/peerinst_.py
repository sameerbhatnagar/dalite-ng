import factory
import pytest

from peerinst.models import AnswerChoice, Question
from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.question.factories import CategoryFactory


class RealisticQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    title = factory.Faker("sentence", nb_words=4)
    text = factory.Faker("paragraph")
    category = factory.RelatedFactory(CategoryFactory)


class RealisticAnswerChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnswerChoice

    text = factory.Faker("paragraph")


@pytest.fixture
def realistic_questions():
    questions = [RealisticQuestionFactory() for i in range(1, 20)]
    for q in questions:
        [
            RealisticAnswerChoiceFactory(question=q, correct=j == 2)
            for j in range(1, 4)
        ]

    return questions
