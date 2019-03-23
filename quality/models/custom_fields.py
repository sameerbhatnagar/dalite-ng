from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProbabilityField(models.FloatField):
    description = _("Probability between 0 and 1")
    default_error_messages = {
        "invlid": _("'%(value)s' value must be a float between 0 and 1.")
    }

    def get_internal_type(self):
        return "ProbabilityField"

    def to_python(self, val):
        val = super(ProbabilityField, self).to_python(val)
        if not 0 <= val <= 1:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": val},
            )
