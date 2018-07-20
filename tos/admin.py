from django.contrib import admin

from . import models

admin.register(models.Tos)
admin.register(models.Consent)


@admin.register(models.Tos)
class TosAdmin(admin.ModelAdmin):
    list_display = ['version','text','created','current','role']
    search_fields = ['text']


@admin.register(models.Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ['user','tos','accepted','datetime']
    search_fields = ['user']   
