import factory
import pytest
import random
from timeit import default_timer as timer

from django.test import TestCase

from peerinst import models
from peerinst.tests.factories import (
    AnswerFactory,
    QuestionFactory,
    UserFactory,
)


class QuestionTestCase(TestCase):
    def setUp(self):
        """
        Make questions, but do not generate answers as factory does not add
        a user by default.

        Make users each with an answer to each question (using Faker to
        make rationale text).
        """
        print("Populating test db...")

        for i in range(1, self.N_questions + 1):
            q = QuestionFactory(choices=5, choices__correct=[2, 3])
            for j in range(1, self.N_answers + 1):
                u = UserFactory()
                a = AnswerFactory(
                    question=q,
                    user_token=u.username,
                    first_answer_choice=random.choice(
                        list(range(1, self.N_choices + 1))
                    ),
                    second_answer_choice=random.choice(
                        list(range(1, self.N_choices + 1))
                    ),
                    rationale=factory.Faker("sentence", nb_words=10),
                )
            print(("{}%".format(float(i) / self.N_questions * 100)))

            assert (
                models.Answer.objects.filter(question=q).count()
                == self.N_answers
            )
        assert models.Question.objects.count() == self.N_questions


class QuestionMethodTests(QuestionTestCase):
    N_questions = 1
    N_answers = 1000
    N_choices = 5
    N_correct = 2

    def setUp(self):
        super(QuestionMethodTests, self).setUp()

    @pytest.mark.skip(reason="Performance test; not needed for CI.")
    def test_get_matrix(self):
        """
        Current benchmarks (runserver):
            - 100 questions with 100 answers in <1s. (This test is very slow.)
            - 1 question with 1000 answers is 0.047s --> ~5s for 100 questions.
        """
        print("Timing get_matrix function...")

        matrices = []
        start = timer()
        for q in models.Question.objects.all():
            matrices.append(q.get_matrix())
        end = timer()

        print(("Total time = " + str(end - start)))
        print(
            (
                "Avg time per question = "
                + str((end - start) / self.N_questions)
            )
        )

        """
        Check results based on probability of each quadrant of matrix.
        Should be valid for large N_answers (at least within ~10% tolerance).
        """
        print("Checking matrix values...")
        prob = float(self.N_correct) / self.N_choices

        for m in matrices:
            print((m["easy"]))
            print((m["hard"]))
            print((m["tricky"]))
            print((m["peer"]))
            self.assertTrue(
                abs(1 - m["easy"] - m["hard"] - m["tricky"] - m["peer"])
                <= 0.01
            )
            self.assertTrue(abs(m["easy"] / (prob * prob) - 1) <= 0.1)
            self.assertTrue(
                abs(m["hard"] / ((1 - prob) * (1 - prob)) - 1) <= 0.1
            )
            self.assertTrue(abs(m["tricky"] / (prob * (1 - prob)) - 1) <= 0.1)
            self.assertTrue(abs(m["peer"] / ((1 - prob) * prob) - 1) <= 0.1)
