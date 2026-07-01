from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import EmailOTP, User, UserOnboarding


@admin.register(User)
class RehaishUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rehaish profile", {"fields": ("role", "phone", "city", "email_verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Rehaish profile",
            {"fields": ("email", "role", "phone", "city", "email_verified")},
        ),
    )
    list_display = (
        "email",
        "username",
        "role",
        "email_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "email_verified", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name", "phone")


@admin.register(UserOnboarding)
class UserOnboardingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "cnic_number",
        "status",
        "cnic_format_valid",
        "cnic_images_present",
        "cnic_verified",
        "submitted_at",
    )
    list_filter = ("status", "cnic_verified", "gender", "submitted_at")
    search_fields = ("user__email", "user__username", "cnic_number")
    readonly_fields = ("submitted_at", "updated_at")


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "purpose",
        "expires_at",
        "consumed_at",
        "attempts",
        "created_at",
    )
    list_filter = ("purpose", "created_at", "consumed_at")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("code_hash", "created_at")
