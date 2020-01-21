# -*- coding: utf-8 -*-


import logging

from django.apps import AppConfig
from django.db.utils import OperationalError
from django.utils.translation import ugettext_lazy as _


class PeerinstConfig(AppConfig):
    name = "peerinst"
    verbose_name = _("Dalite Peer Instruction")

    def ready(self):
        import peerinst.signals  # noqa
        from django_lti_tool_provider.views import LTIView  # noqa

        from .lti import ApplicationHookManager  # noqa
        from .scheduled import start_scheduled_events

        LTIView.register_authentication_manager(ApplicationHookManager())

        try:
            start_scheduled_events()
        except OperationalError:
            logging.getLogger("peerinst-scheduled").warning(
                "The migrations have to be run before the scheduled event "
                "may work."
            )
