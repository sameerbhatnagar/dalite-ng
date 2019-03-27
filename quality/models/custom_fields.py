import re

from django.contrib.admin.widgets import AdminTextareaWidget
from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProbabilityField(models.FloatField):
    description = _("Probability between 0 and 1")


class ProbabilityField(models.FloatField):
    description = _("Probability between 0 and 1")
    default_error_messages = {
        "invlid": _("'%(value)s' value must be a float between 0 and 1.")
    }

    def to_python(self, val):
        val = super(ProbabilityField, self).to_python(val)
        if not 0 <= val <= 1:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": val},
            )
        return val


class CommaSepField(models.TextField):
    description = _("Comma separated list")
    default_error_messages = {
        "invalid": _("'%(value)s' value must be a comma separated string.")
    }

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super(CommaSepField, self).__init__(*args, **kwargs)

    def to_python(self, val):
        print(4)
        if not val:
            return []

        if isinstance(val, list):
            return val

        return [v.strip() for v in val.split(",")]

    def from_db_value(self, val, *args):
        print(3)
        return self.to_python(val)

    def get_prep_value(self, val):
        print(2)
        return ",".join(val)

    def value_to_string(self, obj):
        print(1)
        val = self._get_val_from_obj(obj)
        return self.get_db_prep_value(val)

    def formfield(self, **kwargs):
        defaults = kwargs
        if defaults["widget"] == AdminTextareaWidget:
            defaults["widget"] = AdminCommaSepFieldWidget
        return super(CommaSepField, self).formfield(**defaults)


class AdminCommaSepFieldWidget(AdminTextareaWidget):
    def format_value(self, val):
        val = super(AdminCommaSepFieldWidget, self).format_value(val)
        return ", ".join(
            re.sub(r"u?'(?!,|\])|'(?=,|\])", "", val[1:-1]).split(",")
        )
