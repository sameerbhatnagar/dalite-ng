import random
from peerinst.models import Assignment


def new_assignments(n, questions, min_questions=1):
    questions = [questions] if not isinstance(questions, list) else questions

    def generator(min_questions):
        i = 0
        while True:
            i += 1
            yield {
                "identifier": "assignment{}".format(i),
                "title": "assignment{}".format(i),
                "questions": random.sample(
                    questions, k=random.randint(min_questions, len(questions))
                ),
            }

    gen = generator(min_questions)
    return [next(gen) for _ in range(n)]


def add_assignments(assignments):
    assignments_ = [
        Assignment.objects.create(
            **{k: v for k, v in a.items() if k != "questions"}
        )
        for a in assignments
    ]
    for assignment, a in zip(assignments_, assignments):
        assignment.questions.add(*a["questions"])
    return assignments_
