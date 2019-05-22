# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess
import threading
from datetime import datetime, timedelta


def start_scheduled_events():
    """
    Starts all events which happen at specific times or dates.
    """
    update_reputation_history()


def update_reputation_history(update_now=False):
    """
    Starts a timer calling this function at midnight. If `update_now` is True,
    will start a background python process updating all reputations.

    Parameters
    ----------
    update_now : bool (default : False)
        If the reputations should be updated
    """
    if update_now:
        python_cmd = subprocess.check_output(["which", "python"])
        manage_file = os.path.join(
            os.path.dirname(__file__), os.pardir, "manage.py"
        )
        process = subprocess.Popen(
            [python_cmd, manage_file, "update_reputation_history"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    midnight = datetime.now() + timedelta(days=1)
    midnight.replace(hour=0, minute=0, second=0, microsecond=0)

    timer = threading.Timer(
        (midnight - datetime.now()).seconds,
        lambda: update_reputation_history(True),
    )
    timer.setDaemon(True)
    timer.start()
