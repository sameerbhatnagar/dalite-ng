from quality.models import RightAnswerCriterion, RightAnswerCriterionRules


def new_right_answer_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": []}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_right_answer_rules(n):
    def generator():
        while True:
            yield {"threshold": 1}

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_right_answer_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [RightAnswerCriterion.objects.create(**d) for d in data]


def add_right_answer_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [RightAnswerCriterionRules.get_or_create(**d) for d in data]
