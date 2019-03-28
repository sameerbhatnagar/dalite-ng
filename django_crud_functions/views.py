# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from dalite.views.errors import response_400, response_500


@require_POST
def create(req, model, logger=None, return_instance=False):
    """
    View to create a new instance of `model`. Needs to be a POST request with
    data:
        - "data": Dict[str, Any]
            Initial data for the instance

    Parameters
    ----------
    req : HttpRequest
        Post request
    model : Model
        Django model
    logger : Optional[Logger] (default : None)
        Logger from the logging module if logging is wanted
    return_instance : bool (default : False)
        If the model instance should be returned as dict (`model` needs to
        implement a valid __iter__ method)

    Returns
    -------
    HttpResponse
        Either
            - A 200 JsonResponse with the instance data in a json object
            - An empty 200 HttpResponse
            - An error HttpResponse
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning if logger else None,
        )

    try:
        data = data["data"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning if logger else None,
        )

    if not isinstance(data, dict) or any(
        not isinstance(field, str) for field in data
    ):
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=("data wasn't a valid dict; was {}.".format(data)),
            log=logger.warning if logger else None,
        )

    # TODO Wrap in try except
    instance = model.objects.create(**data)

    if logger:
        logger.info(
            "Instance of model %s created with primary key %d and data %s.",
            model,
            instance.pk,
            data,
        )

    if return_instance:
        try:
            return JsonResponse(dict(instance), status=201)
        except TypeError:
            return response_500(
                req,
                msg="",
                logger_msg=(
                    "The model {} doesn't have a __iter__ method".format(model)
                    + " and so can't be returned."
                ),
                log=logger.warning if logger else None,
            )
    else:
        return HttpResponse(status=201)


@require_POST
def update(req, model, logger=None, return_instance=False):
    """
    View to modify an instance of `model`. Needs to be a POST request with
    data:
        - "pk": int
            Primary key of the instance to modify
        - "data": Dict[str, Any]
            Data to update

    Parameters
    ----------
    req : HttpRequest
        Post request
    model : Model
        Django model
    logger : Optional[Logger] (default : None)
        Logger from the logging module if logging is wanted
    return_instance : bool (default : False)
        If the model instance should be returned as dict (`model` needs to
        implement a valid __iter__ method)

    Returns
    -------
    HttpResponse
        Either
            - A 200 JsonResponse with the instance data in a json object
            - An empty 200 HttpResponse
            - An error HttpResponse
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning if logger else None,
        )

    try:
        pk = data["pk"]
        data = data["data"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning if logger else None,
        )

    if not isinstance(pk, int):
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(
                "pk wasn't an int; was {}, an {}.".format(pk, type(pk))
            ),
            log=logger.warning if logger else None,
        )
    if not isinstance(data, dict) or any(
        not isinstance(field, str) for field in data
    ):
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=("data wasn't a valid dict; was {}.".format(data)),
            log=logger.warning if logger else None,
        )

    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(
                "There is no {} with primary key {}.".format(model, pk)
            ),
            log=logger.warning if logger else None,
        )

    try:
        old_values = [getattr(instance, field) for field in data]
    except AttributeError as e:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(str(e)),
            log=logger.warning if logger else None,
        )

    try:
        for field, value in data:
            setattr(instance, field, value)
        instance.save()
    except ValueError:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(
                "One or more of the values {}".format(data)
                + " were of the wrong type for {}.".format(model)
            ),
            log=logger.warning if logger else None,
        )

    values = [getattr(instance, field) for field in data]

    if logger:
        logger.info(
            "Fields %s for %s with pk %d were updated from %s to %s."
            "({})".format(", ".join(f for f in data.keys())),
            model,
            instance.pk,
            "({})".format(", ".join(f for f in old_values.values())),
            "({})".format(", ".join(f for f in values.values())),
        )

    if return_instance:
        try:
            return JsonResponse(dict(instance), status=200)
        except TypeError:
            return response_500(
                req,
                msg="",
                logger_msg=(
                    "The model {} doesn't have a __iter__ method".format(model)
                    + " and so can't be returned."
                ),
                log=logger.warning if logger else None,
            )
    else:
        return HttpResponse(status=200)


@require_POST
def delete(req, model, logger=None):
    """
    View to delete an instance of `model`. Needs to be a POST request with
    data:
        - "pk": int
            Primary key of the instance to modify

    Parameters
    ----------
    req : HttpRequest
        Post request
    model : Model
        Django model
    logger : Optional[Logger] (default : None)
        Logger from the logging module if logging is wanted

    Returns
    -------
    HttpResponse
        Either
            - An empty 200 HttpResponse
            - An error HttpResponse
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning if logger else None,
        )

    try:
        pk = data["pk"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning if logger else None,
        )

    if not isinstance(pk, int):
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(
                "pk wasn't an int; was {}, an {}.".format(pk, type(pk))
            ),
            log=logger.warning if logger else None,
        )

    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong"),
            logger_msg=(
                "There is no {} with primary key {}.".format(model, pk)
            ),
            log=logger.warning if logger else None,
        )

    instance.delete()

    if logger:
        logger.info("%s with pk %d was deleted.", model, pk)

    return HttpResponse(status=200)
