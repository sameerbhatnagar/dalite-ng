from django.db import models

from .group import StudentGroup


class StudentGroupCourse(models.Model):
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    course = models.ForeignKey("course_flow.Course", on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Group-Course Link"
        verbose_name_plural = "Group-Course Links"
