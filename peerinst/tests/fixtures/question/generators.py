from peerinst.models import Question


def new_questions(n):
    def generator():
        i = 0
        while True:
            i += 1
            yield {
                "title": "question{}".format(i),
                "text": "question{}".format(i),
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_questions(questions):
    return [Question.objects.create(**q) for q in questions]
