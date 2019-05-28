# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import operator
import smtplib
from celery import shared_task
from dalite.celery import try_async
from django.core.mail import send_mail

logger = logging.getLogger("peerinst-models")


@try_async
@shared_task
def send_email_async(*args, **kwargs):
    try:
        send_mail(*args, **kwargs)
    except smtplib.SMTPException:
        err = "There was an error sending the email."
        logger.error(err)


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
        f = MetaFeature.objects.get(key="difficulty", value=level)
        s = MetaSearch.objects.create(meta_feature=f, content_object=q)
        q.meta_search.add(s)

        logger.debug("Updating difficulty of '{}''".format(q))
        logger.debug("Feature: {}".format(f))
        logger.debug("Search object: {}".format(s))
        logger.debug(
            "All search objects for question: {}".format(
                "".join([str(_s) for _s in q.meta_search.all()])
            )
        )

        assert q.meta_search.filter(key="difficulty").count() == 1

    return
