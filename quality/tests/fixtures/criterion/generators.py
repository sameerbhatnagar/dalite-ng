from quality.models import MinWordsCriterion


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
