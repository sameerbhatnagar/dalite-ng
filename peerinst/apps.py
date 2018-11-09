# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import apps
from django.utils.translation import ugettext_lazy as _

from .scheduled import start_scheduled_events


class PeerInstConfig(apps.AppConfig):
    name = "peerinst"
    verbose_name = _("Dalite Peer Instruction")

    def ready(self):
        import peerinst.signals  # noqa

        start_scheduled_events()
