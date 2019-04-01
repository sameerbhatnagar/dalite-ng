from quality.models import MinCharsCriterion, MinCharsCriterionRules


def new_min_chars_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": ["min_chars"]}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_min_chars_rules(n):
    def generator():
        i = 0
        while True:
            yield {"threshold": 1, "min_chars": i}
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_min_chars_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinCharsCriterion.objects.create(**d) for d in data]


def add_min_chars_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinCharsCriterionRules.get_or_create(**d) for d in data]
