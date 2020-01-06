from django.db import models

from .teacher import Teacher


class RunningTask(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    description = models.TextField()
    teacher = models.ForeignKey(
        Teacher, related_name="running_tasks", on_delete="CASCADE"
    )
    datetime = models.DateTimeField(auto_now_add=True)
