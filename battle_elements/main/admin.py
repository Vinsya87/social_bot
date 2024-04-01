from django.contrib import admin
from main.models import Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name',]

