import pytest

from .generators import (
    add_likelihood_criterion,
    add_likelihood_rules,
    new_likelihood_criterion,
    new_likelihood_rules,
)


@pytest.fixture
def likelihood_criterion():
    return add_likelihood_criterion(new_likelihood_criterion(1))[0]


@pytest.fixture
def likelihood_rules():
    return add_likelihood_rules(new_likelihood_rules(1))[0]
