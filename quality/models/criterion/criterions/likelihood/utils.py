# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals


def load_print(text):
    print("[*] {}".format(text).ljust(80), end="\r")


def done_print(text):
    print("[+] {}".format(text).ljust(80))
