from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .models import Coordinator, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'username', 'email', 'first_name', 'last_name',]
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'language_code',
                'phone_number',
                'telegram_id',
                'country',
                'city',
                'country_travel',
                'city_travel',
                'additional_info',
                'identification',
                'is_coordinator'),
        }),
    )
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone_number', 'identification', 'additional_info')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('phone_number', 'identification', 'additional_info')}),
    # )
    # form = CustomUserChangeForm


@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    raw_id_fields = ('country', 'city',)
    list_display = ('get_username', 'coordinator_level', 'get_country_name', 'get_city_name')
    filter_horizontal = ('cities',)

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    get_username.short_description = 'Username'

    def get_country_name(self, obj):
        return obj.country.name if obj.country else None
    get_country_name.short_description = 'Country'

    def get_city_name(self, obj):
        return obj.city.name if obj.city else None
    get_city_name.short_description = 'City'

