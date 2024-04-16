from django.contrib import admin
from main.models import City, Config, Country


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['site_name',]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code', 'country_id']
    search_fields = ['name', 'country_code', 'country_id']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code', 'country']
    search_fields = ['name', 'country_code', 'country__name']