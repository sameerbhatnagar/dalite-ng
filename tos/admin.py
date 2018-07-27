from django.contrib import admin

from . import models

admin.register(models.Role)
admin.register(models.Tos)
admin.register(models.Consent)
admin.register(models.EmailType)
admin.register(models.EmailConsent)


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["role"]
    search_fields = ["role"]


@admin.register(models.Tos)
class TosAdmin(admin.ModelAdmin):
    list_display = ["version", "text", "created", "current", "role"]
    search_fields = ["text"]


@admin.register(models.Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ["user", "tos", "accepted", "datetime"]
    search_fields = ["user"]


@admin.register(models.EmailType)
class EmailTypeAdmin(admin.ModelAdmin):
    list_display = ["role", "type"]
    search_fields = ["role", "type"]


@admin.register(models.EmailConsent)
class EmailConsentAdmin(admin.ModelAdmin):
    list_display = ["user", "email_type"]
    search_fields = ["user"]
