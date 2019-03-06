# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


def edit_patterns():
    return [url(r"^edit/$", views.edit.index, name="quality-edit")]


urlpatterns = sum([edit_patterns()], [])
