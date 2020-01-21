import datetime
import random

import factory
import pytz
from django.contrib.auth.models import User
from tos.models import Consent, Tos

from .. import models


class UserFactory(factory.DjangoModelFactory):
    # This class was adapted from
    # edx-platform/common/djangoapps/student/tests/factories.py.
    class Meta:
        model = User
        django_get_or_create = ["username", "email"]

    username = factory.Sequence("robot{0}".format)
    email = factory.Sequence("robot+test+{0}@edx.org".format)
    password = factory.PostGenerationMethodCall("set_password", "test")
    first_name = factory.Sequence("Robot{0}".format)
    last_name = "Test"
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = datetime.datetime(2012, 1, 1, tzinfo=pytz.utc)
    date_joined = datetime.datetime(2011, 1, 1, tzinfo=pytz.utc)

    @factory.post_generation
    def consent(user, create, extracted, **kwargs):
        if not create:
            return

        if Tos.objects.exists():
            consent = Consent(
                user=user, accepted=False, tos=Tos.objects.first()
            )
            consent.save()


class AnswerFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Answer

    rationale = factory.Sequence("Rationale {}".format)


class AnswerChoiceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AnswerChoice

    @factory.post_generation
    def rationales(answer_choice, create, extracted, **kwargs):
        if not create or not extracted:
            assert (
                not extracted
            ), "Cannot generate answers when answer choice is not saved."
            return
        question = answer_choice.question
        choice_index = kwargs.get("index")
        assert (
            choice_index is not None
        ), "Automatic choice index determination not implemented."
        for i in range(extracted):
            AnswerFactory(
                question=question,
                first_answer_choice=choice_index,
                expert=True,
            )


class QuestionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Question

    title = factory.Sequence("Question {}".format)
    text = factory.Sequence("Text for question {}".format)

    @factory.post_generation
    def choices(question, create, extracted, **kwargs):
        if not create or not extracted:
            assert (
                not extracted and not kwargs
            ), "Cannot generate answer choices when question is not saved."
            return
        choice_indices = list(range(1, extracted + 1))
        correct_choices = kwargs.get("correct")
        if correct_choices is None:
            correct_choices = random.sample(
                choice_indices, random.randrange(1, extracted)
            )
        rationales = kwargs.get("rationales")
        for i in choice_indices:
            correct = i in correct_choices
            text = "Choice {} ({}correct)".format(i, "" if correct else "not ")
            AnswerChoiceFactory(
                question=question,
                text=text,
                correct=correct,
                rationales=rationales,
                rationales__index=i,
            )


class AssignmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Assignment

    identifier = factory.Sequence("Assignment{}".format)
    title = factory.Sequence("Assignment title {}".format)

    @factory.post_generation
    def questions(assignment, create, extracted, **kwargs):
        if not create or not extracted:
            assert (
                not extracted
            ), "Cannot generate questions when assignment is not saved."
            return
        for i in range(extracted):
            assignment.questions.add(QuestionFactory())
