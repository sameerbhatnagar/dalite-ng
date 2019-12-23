# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ReputationConfig(AppConfig):
    name = "reputation"
    verbose_name = _("Dalite reputation framework")

    def ready(self):
        from . import signals  # noqa
