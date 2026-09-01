from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class NotifiUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Notifi', {'fields': ('role', 'school', 'phone')}),
    )
    list_display = ('username', 'email', 'role', 'school', 'is_active')
    list_filter = ('role', 'is_active')
