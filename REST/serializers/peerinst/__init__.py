__all__ = [
    "AssignmentSerializer",
    "AnswerSerializer",
    "DisciplineSerializer",
    "FeedbackReadSerialzer",
    "FeedbackWriteSerialzer",
    "QuestionSerializer",
    "RankSerializer",
    "StudentGroupAssignmentAnswerSerializer",
    "TeacherSerializer",
]

from .assignment import (
    AssignmentSerializer,
    DisciplineSerializer,
    QuestionSerializer,
    RankSerializer,
)  # noqa
from .answer import (
    AnswerSerializer,
    FeedbackReadSerialzer,
    FeedbackWriteSerialzer,
    StudentGroupAssignmentAnswerSerializer,
)  # noqa
from .teacher import TeacherSerializer
