from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from ..generators import (
    add_assignments,
    add_groups,
    new_student_group_assignments,
    new_teachers,
    new_assignments,
    new_groups,
    new_student_group_assignments,
    new_teachers,
)


class TestGroupDetailsPage(TestCase):
    def setUp(self):
        self.client = Client()
