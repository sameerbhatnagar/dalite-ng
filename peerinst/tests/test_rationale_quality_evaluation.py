from peerinst.rationale_quality_evaluation import evaluate_quality
from quality.tests.fixtures import global_quality  # noqa

from .fixtures import *  # noqa


def test_evaluate_quality__global_quality_answer_str_passes(global_quality):
    answer = ". " * dict(global_quality)["min_words"]["value"]
    err = evaluate_quality(answer)
    assert err is None


def test_evaluate_quality__global_quality_answer_Answer_passes(
    global_quality, answers
):
    answer = answers[0]
    answer.rationale = ". " * dict(global_quality)["min_words"]["value"]
    err = evaluate_quality(answer)
    assert err is None


def test_evaluate_quality__global_quality_answer_str_fails(global_quality):
    answer = ". " * (dict(global_quality)["min_words"]["value"] - 1)
    err = evaluate_quality(answer)
    assert isinstance(err, basestring)
    assert "min_words" in err


def test_evaluate_quality__global_quality_answer_Answer_fails(
    global_quality, answers
):
    answer = answers[0]
    answer.rationale = ". " * (dict(global_quality)["min_words"]["value"] - 1)
    err = evaluate_quality(answer)
    assert isinstance(err, basestring)
    assert "min_words" in err
