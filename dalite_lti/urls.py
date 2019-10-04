# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


def dalite_lti_patterns():
    return [url(r"^$", views.index, name="index")]


urlpatterns = sum([dalite_lti_patterns()], [])
