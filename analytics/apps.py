# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AnalyticsConfig(AppConfig):
    name = "analytics"
    verbose_name = _("Dalite analytics")

    def ready(self):
        from . import signals  # noqa
