import numpy as np
from django.db.models import Max
from django.utils.translation import ugettext

from tos.models import Consent

from .models import Answer


def choose_rationales(
    quality, first_answer_choice, rationale, question, seed=None, n_choices=4
):
    if seed is not None:
        np.random.seed(seed)

    first_choice = first_answer_choice
    answer_choices = question.answerchoice_set.all()

    # users who didn't accept the TOS
    usernames_to_exclude = (
        Consent.objects.filter(tos__role="student")
        .values("user__username")
        .annotate(Max("datetime"))
        .filter(accepted=False)
        .values_list("user__username")
    )

    all_answers = Answer.objects.filter(
        question=question, show_to_others=True
    ).exclude(user_token__in=usernames_to_exclude)

    if answer_choices[first_choice - 1].correct:
        other_answers = all_answers.exclude(first_answer_choice=first_choice)

        try:
            # pick a random answer as the other answer choice. This has the
            # effect of making popular answer choices more likely to be picked.
            # randint is used other choice to avoid fetching all rationales.
            second_choice = other_answers[
                np.random.randint(other_answers.count())
            ].first_answer_choice
        except ValueError:
            raise RationaleSelectionError(
                ugettext(
                    """Can't proceed since the course staff did not
                    provide example answers."""
                )
            )

    else:
        second_choice = np.random.choice(
            [a for a in answer_choices if a.correct]
        )

    chosen_rationales = []
    for choice in (first_choice, second_choice):

        label = question.get_choice_label(choice)

        answers = all_answers.filter(first_answer_choice=choice)

        if answers:

            scores = [quality.evaluate(answer)[0] for answer in answers]
            sum_scores = sum(scores)
            scores = [score / sum_scores for score in scores]

            answers = [
                answers[i]
                for i in np.random.choice(
                    range(len(scores)),
                    replace=False,
                    size=min(n_choices, len(scores)),
                    p=scores,
                )
            ]
            rationales = [(answer.id, answer.rationale) for answer in answers]
        else:

            rationales = []

        chosen_rationales.append((choice, label, rationales))

    chosen_rationales[0][2].append(
        (None, ugettext("I stick with my own rationale."))
    )

    return chosen_rationales


class RationaleSelectionError(Exception):
    pass
