from __future__ import unicode_literals

from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from peerinst.models import StudentGroup, StudentGroupAssignment, Teacher


def group_access_required(fct):
    def wrapper(req, *args, **kwargs):
        group_hash = kwargs.get("group_hash", None)
        assignment_hash = kwargs.get("assignment_hash", None)
        return_assignment = assignment_hash is not None

        if group_hash is None and assignment_hash is None:
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _("You don't have access to this resource.")
                },
            )
            return HttpResponseForbidden(resp.render())

        try:
            teacher = Teacher.objects.get(user=req.user)
        except Teacher.DoesNotExist:
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _("You don't have access to this resource.")
                },
            )
            return HttpResponseForbidden(resp.render())

        if group_hash is not None:
            group = StudentGroup.get(group_hash)
            if group is None:
                resp = TemplateResponse(
                    req,
                    "400.html",
                    context={
                        "message": _(
                            'There is no group with hash "{}".'.format(
                                group_hash
                            )
                        )
                    },
                )
                return HttpResponseBadRequest(resp.render())

        else:
            assignment = StudentGroupAssignment.get(assignment_hash)
            if assignment is None:
                resp = TemplateResponse(
                    req,
                    "400.html",
                    context={
                        "message": _(
                            'There is no assignment with hash "{}".'.format(
                                assignment_hash
                            )
                        )
                    },
                )
                return HttpResponseBadRequest(resp.render())
            group = assignment.group

        if teacher not in group.teacher.all():
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _(
                        "You don't have access to this resource. You must be "
                        "registered as a teacher for the group {}.".format(
                            group.name
                        )
                    )
                },
            )
            return HttpResponseForbidden(resp.render())

        if return_assignment:
            return fct(
                req,
                *args,
                teacher=teacher,
                group=group,
                assignment=assignment,
                **kwargs
            )
        else:
            return fct(req, *args, teacher=teacher, group=group, **kwargs)

    return wrapper


def teacher_required(fct):
    def wrapper(req, *args, **kwargs):
        if not Teacher.objects.filter(user=req.user).exists():
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _("You don't have access to this resource.")
                },
            )
            return HttpResponseForbidden(resp.render())
        return fct(req, *args, **kwargs)

    return wrapper
