from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .models import Coordinator, Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'username', 'email', 'first_name', 'last_name',]
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone_number', 'identification', 'additional_info')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('phone_number', 'identification', 'additional_info')}),
    # )
    # form = CustomUserChangeForm


@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'coordinator_level')
    search_fields = ('user__username',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name')
    search_fields = ('user__username',)
