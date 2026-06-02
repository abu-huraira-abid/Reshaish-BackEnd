from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class RehaishUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rehaish profile", {"fields": ("role", "phone", "city")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rehaish profile", {"fields": ("email", "role", "phone", "city")}),
    )
    list_display = ("email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
