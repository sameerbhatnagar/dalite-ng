from quality.models import Quality


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

    quality_, evaluation = quality.evaluate(answer)

    if quality_ < quality.threshold:
        failed = [
            c["name"] for c in evaluation if c["quality"] < c["threshold"]
        ]
        return (
            "Your rationale didn't pass the following criterions:"
            "\n\t{}".format("\n\t".join(failed))
        )

    return None
