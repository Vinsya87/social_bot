from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserChangeForm

User = get_user_model()

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'groups', 'user_permissions')
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
            'user_permissions': FilteredSelectMultiple('Разрешения', is_stacked=False),
        }