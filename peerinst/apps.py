# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django import apps
from django.db.utils import OperationalError
from django.utils.translation import ugettext_lazy as _

from .scheduled import start_scheduled_events


class PeerInstConfig(apps.AppConfig):
    name = "peerinst"
    verbose_name = _("Dalite Peer Instruction")

    def ready(self):
        import peerinst.signals  # noqa

        try:
            start_scheduled_events()
        except OperationalError:
            logging.getLogger("peerinst-scheduled").warning(
                "The migrations have to be run before the scheduled event "
                "may work."
            )
