from .min_words import MinWordsCriterion


def criterions():
    """
    Gives a dict with criterion name as key and criterion class as value

    Returns
    -------
    Dict[str, Model]
        Criterion name to criterion class
    """
    return {"min_words": MinWordsCriterion}
