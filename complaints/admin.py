from django.contrib import admin

from .models import Complaint, ComplaintHistory, User


class HistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ("previous_status", "new_status", "note", "changed_by", "changed_at")
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("email", "name")
    fields = ("email", "name", "role", "is_active", "is_superuser", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("complaint_id", "title", "category", "status", "priority", "user", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("complaint_id", "title", "user__email")
    readonly_fields = ("complaint_id", "created_at", "updated_at")
    inlines = [HistoryInline]
