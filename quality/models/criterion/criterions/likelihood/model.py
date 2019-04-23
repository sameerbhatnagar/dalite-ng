# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import partial
from itertools import chain
from math import exp, log

from .data import read_data


def create_model(language, other_language=None, max_gram=3):
    data = {
        gram: val
        for gram, val in read_data(language).items()
        if gram <= max_gram
    }
    if other_language is None:
        other = {
            gram: {g: 1.0 / len(val) for g in val.keys()}
            for gram, val in data.items()
        }
    else:
        other = {
            gram: val
            for gram, val in read_data(other_language).items()
            if gram <= max_gram
        }

    return partial(predict, data=data, other=other)


def predict(text, data, other):

    l1 = log_likelihood(text, data)
    l0 = log_likelihood(text, other)

    return 1 - min(1, exp(l0 - l1))


def log_likelihood(text, ngrams):
    text = "".join(c for c in text.lower() if c == " " or c in ngrams[1])
    words = [
        [c for c in word.lower() if c in ngrams[1]] for word in text.split()
    ]

    if len(ngrams) == 1:
        return sum(
            sum(
                log(ngrams[1].get(word[i], 1e-16)) + 1e-16
                for i in range(len(word))
            )
            for word in words
        )
    else:
        return sum(
            sum(
                chain(
                    (log(ngrams[1].get(word[0], 1e-16)) + 1e-16,),
                    (
                        log(
                            ngrams[i].get("".join(word[:i]), 1e-16)
                            / ngrams[i - 1].get("".join(word[: i - 1]), 1e-16)
                        )
                        + 1e-16
                        for i in range(2, min(len(ngrams), len(word) + 1))
                    ),
                    (
                        log(
                            ngrams[len(ngrams)].get(
                                "".join(word[i : i + len(ngrams)]), 1e-16
                            )
                            / ngrams[len(ngrams) - 1].get(
                                "".join(word[i : i + len(ngrams) - 1]), 1e-16
                            )
                        )
                        + 1e-16
                        for i in range(len(word) - len(ngrams) + 1)
                    ),
                )
            )
            for word in words
        )
