from quality.models import MinWordsCriterion, MinWordsCriterionRules


def new_min_words_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": "min_words"}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_min_words_rules(n):
    def generator():
        i = 0
        while True:
            yield {"min_words": i}
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_min_words_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinWordsCriterion.objects.create(**d) for d in data]


def add_min_words_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinWordsCriterionRules.get_or_create(**d) for d in data]
