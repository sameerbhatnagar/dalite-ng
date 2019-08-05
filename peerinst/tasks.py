# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import operator

from celery import shared_task

from dalite.celery import try_async

logger = logging.getLogger("peerinst-models")


@shared_task
def update_question_meta_search_difficulty():
    # Prevent circular import
    from peerinst.models import Question, MetaFeature, MetaSearch

    qs = Question.objects.all()
    difficulty_levels = qs[0].get_matrix().keys()
    for d in difficulty_levels:
        f, created = MetaFeature.objects.get_or_create(
            key="difficulty", value=d, type="S"
        )
        if created:
            logger.info("New difficulty level created: {}".format(f))

    for q in qs:
        level = max(q.get_matrix().iteritems(), key=operator.itemgetter(1))[0]
        f = MetaFeature.objects.get(key="difficulty", value=level, type="S")
        s = MetaSearch.objects.create(meta_feature=f, content_object=q)
        q.meta_search.add(s)

        logger.info("Updating difficulty of '{}''".format(q))
        logger.info("Feature: {}".format(f))
        logger.info("Search object: {}".format(s))

        assert (
            q.meta_search.filter(meta_feature__key="difficulty").count() == 1
        )


@try_async
@shared_task
def distribute_assignment_to_students_async(student_group_assignment_pk):
    # Prevent circular import
    from peerinst.models import StudentGroupAssignment

    student_group_assignment = StudentGroupAssignment.objects.get(
        pk=student_group_assignment_pk
    )
    for student in student_group_assignment.group.student_set.all():
        logger.info(
            "Adding assignment %d for student %d",
            student_group_assignment.pk,
            student.pk,
        )
        student.add_assignment(student_group_assignment)
