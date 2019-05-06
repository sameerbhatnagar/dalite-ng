# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .reputation_type import ReputationType


class Reputation(models.Model):
    reputation_type = models.ForeignKey(ReputationType)

    def __str__(self):
        return "{} for {}: {}".format(
            self.pk,
            self.reputation_type,
            str(
                getattr(self, "{}_set".format(self.quality_type.type)).first()
            ),
        )
