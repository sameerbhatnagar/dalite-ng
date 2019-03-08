# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from . import models

admin.site.register(models.MinCharsCriterion)
admin.site.register(models.MinCharsCriterionRules)
admin.site.register(models.MinWordsCriterion)
admin.site.register(models.MinWordsCriterionRules)
admin.site.register(models.Quality)
admin.site.register(models.QualityType)
admin.site.register(models.UsesCriterion)
