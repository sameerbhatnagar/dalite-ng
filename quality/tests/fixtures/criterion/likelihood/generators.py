from quality.models import LikelihoodCriterion, LikelihoodCriterionRules


def new_likelihood_criterion(n):
    def generator():
        while True:
            yield {"uses_rules": ["languages", "max_gram"]}

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_likelihood_rules(n):
    def generator():
        i = 0
        while True:
            yield {
                "threshold": 1,
                "languages": ["english", "french"],
                "max_gram": 3,
            }
            i += 1

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_likelihood_criterion(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [LikelihoodCriterion.objects.create(**d) for d in data]


def add_likelihood_rules(data):
    data = data if hasattr(data, "__iter__") else [data]
    return [LikelihoodCriterionRules.get_or_create(**d) for d in data]
