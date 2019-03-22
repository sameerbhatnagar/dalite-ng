from quality.models import Quality, RejectedAnswer

from .models import Answer


def evaluate_quality(answer, quality=None):
    """
    Evaluates the answer using the given quality or the global one if None are
    given.

    Parameters
    ----------
    answer : Answer
        Answer to evaluate
    quality : Optional[Quality]
        Used quality if given

    Returns
    -------
    Optional[str]
        Error message or None
    """
    if quality is None:
        quality = Quality.objects.get(quality_type__type="global")

    if isinstance(answer, Answer):
        answer = answer.rationale

    quality_, evaluation = quality.evaluate(answer)
    if quality_ is not None and quality_ < quality.threshold:
        failed = [
            c["name"]
            for c in evaluation
            if c["quality"]["quality"] < c["quality"]["threshold"]
        ]
        RejectedAnswer.add(quality, answer, evaluation)
        return (
            "Your rationale didn't pass the following criterions: "
            "{}".format(", ".join(failed))
        )
    return None
