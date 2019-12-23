# -*- coding: utf-8 -*-


from django.conf.urls import url

from . import views


def reputation_patterns():
    return [
        url(r"^teachers/$", views.teachers.index, name="teachers"),
        url(
            r"^teachers/criteria$",
            views.teachers.get_reputation_criteria_list,
            name="teachers--criteria",
        ),
        url(
            r"^teachers/teachers$",
            views.teachers.get_teacher_list,
            name="teachers--teachers",
        ),
        url(
            r"^teachers/teacher$",
            views.teachers.get_teacher_information,
            name="teachers--teacher",
        ),
    ]


urlpatterns = sum([reputation_patterns()], [])
