from peerinst.models import Question, RationaleOnlyQuestion


def new_questions(n, teacher):
    def generator():
        i = 0
        while True:
            i += 1
            yield {
                "title": "question{}".format(i),
                "text": "question{}".format(i),
                "user": teacher.user,
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_questions(questions):
    return [Question.objects.get_or_create(**q)[0] for q in questions]


def add_rationale_only_questions(questions):
    return [
        RationaleOnlyQuestion.objects.get_or_create(**q)[0] for q in questions
    ]
