__all__ = [
    "admin",
    "assert_",
    "assignment",
    "browser",
    "category",
    "discipline",
    "inactive_user",
    "min_words_criterion",
    "min_words_rules",
    "new_teacher",
    "quality_min_words",
    "questions",
    "realistic_questions",
    "student_reputation_with_criteria",
    "teacher",
    "tos_teacher",
    "assignment",
]

from .peerinst_ import (
    admin,
    assignment,
    category,
    discipline,
    inactive_user,
    new_teacher,
    questions,
    realistic_questions,
    teacher,
    tos_teacher,
)
from .quality_ import min_words_criterion, min_words_rules, quality_min_words
from .reputation_ import student_reputation_with_criteria
from .utils import assert_, browser
