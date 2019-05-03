from quality.models import NegWordsCriterion, NegWordsCriterionRules


def new_neg_words_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": ["neg_words"]}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_neg_words_rules(n):
    def generator():
        i = 0
        while True:
            yield {"threshold": 1, "neg_words": [str(j) for j in range(i)]}
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_neg_words_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [NegWordsCriterion.objects.create(**d) for d in data]


def add_neg_words_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [NegWordsCriterionRules.get_or_create(**d) for d in data]
