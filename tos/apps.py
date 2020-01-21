# -*- coding: utf-8 -*-


from django import apps
from django.utils.translation import ugettext_lazy as _


class TosConfig(apps.AppConfig):
    name = "tos"
    verbose_name = _("Dalite user consents")

    def ready(self):
        import tos.signals  # noqa
