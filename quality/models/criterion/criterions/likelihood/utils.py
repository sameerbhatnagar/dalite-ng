# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

logger = logging.getLogger("quality")


def load_print(text):
    logger.debug("[*] {}".format(text))


def done_print(text):
    logger.debug("[+] {}".format(text))
