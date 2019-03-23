from peerinst.quality_evaluation import evaluate_quality
from quality.models import RejectedAnswer
from quality.tests.fixtures import global_quality  # noqa

from .fixtures import *  # noqa


def test_evaluate_quality__global_quality_answer_str_passes(global_quality):
    answer = ". " * dict(global_quality)["min_words"]["value"]
    n_bad = RejectedAnswer.objects.count()
    err = evaluate_quality(answer)
    assert err is None
    assert RejectedAnswer.objects.count() == n_bad


def test_evaluate_quality__global_quality_answer_Answer_passes(
    global_quality, answers
):
    answer = answers[0]
    answer.rationale = ". " * dict(global_quality)["min_words"]["value"]
    n_bad = RejectedAnswer.objects.count()
    err = evaluate_quality(answer)
    assert err is None
    assert RejectedAnswer.objects.count() == n_bad


def test_evaluate_quality__global_quality_answer_str_fails(global_quality):
    answer = ". " * (dict(global_quality)["min_words"]["value"] - 1)
    n_bad = RejectedAnswer.objects.count()
    err = evaluate_quality(answer)
    assert isinstance(err, basestring)
    assert "min_words" in err
    assert RejectedAnswer.objects.count() == n_bad + 1


def test_evaluate_quality__global_quality_answer_Answer_fails(
    global_quality, answers
):
    answer = answers[0]
    answer.rationale = ". " * (dict(global_quality)["min_words"]["value"] - 1)
    n_bad = RejectedAnswer.objects.count()
    err = evaluate_quality(answer)
    assert isinstance(err, basestring)
    assert "min_words" in err
    assert RejectedAnswer.objects.count() == n_bad + 1
