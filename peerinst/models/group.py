import base64
from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


from .question import Discipline
from quality.models import Quality


def current_year():
    return date.today().year


def current_semester():
    current_month = date.today().month
    if current_month < 6:
        return StudentGroup.WINTER
    elif current_month > 7:
        return StudentGroup.FALL
    else:
        return StudentGroup.SUMMER


def max_value_current_year(value):
    return MaxValueValidator(current_year() + 1)(value)


class StudentGroup(models.Model):

    FALL = "FALL"
    SUMMER = "SUMMER"
    WINTER = "WINTER"

    SEMESTER_CHOICES = (
        (FALL, "Fall"),
        (SUMMER, "Summer"),
        (WINTER, "Winter"),
    )

    name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    creation_date = models.DateField(blank=True, null=True, auto_now=True)
    teacher = models.ManyToManyField("Teacher", blank=True)
    student_id_needed = models.BooleanField(default=False)
    quality = models.ForeignKey(
        Quality, blank=True, null=True, on_delete=models.SET_NULL
    )
    semester = models.CharField(
        max_length=6, choices=SEMESTER_CHOICES, default=current_semester
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2015), max_value_current_year],
        default=current_year,
    )

    discipline = models.ForeignKey(
        Discipline, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        if not self.title:
            return self.name
        else:
            return self.title

    class Meta:
        ordering = ["-creation_date"]
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    @staticmethod
    def get(hash_):
        try:
            id_ = int(base64.urlsafe_b64decode(hash_.encode()).decode())
        except UnicodeDecodeError:
            id_ = None
        if id_:
            try:
                group = StudentGroup.objects.get(id=id_)
            except StudentGroup.DoesNotExist:
                group = None
        else:
            group = None

        return group

    @property
    def hash(self):
        return base64.urlsafe_b64encode(str(self.id).encode()).decode()

    @property
    def students(self):
        return self.student_set.all()

    @property
    def has_emails(self):
        return all(s.student.email for s in self.students)
