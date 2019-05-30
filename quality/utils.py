# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.utils.encoding import force_text


# https://stackoverflow.com/questions/19734724/django-is-not-json-serializable-when-using-ugettext-lazy
class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)
