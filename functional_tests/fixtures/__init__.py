__all__ = [
    "assert_",
    "assignment",
    "browser",
    "category",
    "discipline",
    "min_words_criterion",
    "min_words_rules",
    "quality_min_words",
    "questions",
    "teacher",
    "tos_teacher",
]

from .peerinst_ import (
    assignment,
    category,
    discipline,
    questions,
    teacher,
    tos_teacher,
)
from .quality_ import min_words_criterion, min_words_rules, quality_min_words
from .utils import assert_, browser
