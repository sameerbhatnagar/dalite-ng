# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import smtplib

from celery import shared_task

from django.core.mail import send_mail

logger = logging.getLogger("peerinst-models")


@shared_task
def send_email_async(*args, **kwargs):
    try:
        send_mail(*args, **kwargs)
    except smtplib.SMTPException:
        err = "There was an error sending the email."
        logger.error(err)
