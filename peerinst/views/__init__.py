__all__ = ["admin_", "group", "question_", "student", "teacher"]

<<<<<<< Updated upstream
=======
from . import admin_, group, question_, student, teacher
>>>>>>> Stashed changes
from .assignment import *  # noqa
from .collection import *  # noqa
from .group import *  # noqa
from .search import *  # noqa
from .standalone_views import *  # noqa
from .views import *  # noqa

from . import group, question_, student, teacher

from .research import *  # noqa; noqa
