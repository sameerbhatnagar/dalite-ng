from quality.models import (
    SelectedAnswerCriterion,
    SelectedAnswerCriterionRules,
)


def new_selected_answer_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": ["default_if_never_shown"]}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_selected_answer_rules(n):
    def generator():
        while True:
            yield {"threshold": 1, "default_if_never_shown": 0}

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_selected_answer_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [SelectedAnswerCriterion.objects.create(**d) for d in data]


def add_selected_answer_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [SelectedAnswerCriterionRules.get_or_create(**d) for d in data]
