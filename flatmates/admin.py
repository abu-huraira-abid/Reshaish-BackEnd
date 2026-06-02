from django.contrib import admin

from flatmates.models import FlatmateProfile


@admin.register(FlatmateProfile)
class FlatmateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "budget", "match_visibility")
    list_filter = ("city", "match_visibility")
    search_fields = ("user__email", "city", "bio")
