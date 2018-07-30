from __future__ import unicode_literals

from django import apps
from django.utils.translation import ugettext_lazy as _


class ConsentConfig(apps.AppConfig):
    name = "tos"
    verbose_name = _("Dalite user consents")

    def ready(self):
        import tos.signals
