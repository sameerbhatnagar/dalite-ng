from quality.models import MinCharsCriterion, MinWordsCriterion


def new_min_words_criterion(n):
    def generator():
        i = 0
        while True:
            yield {"min_words": i}
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_min_words_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinWordsCriterion.create(**d) for d in data]


def new_min_chars_criterion(n):
    def generator():
        i = 0
        while True:
            yield {"min_chars": i}
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_min_chars_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [MinCharsCriterion.create(**d) for d in data]
