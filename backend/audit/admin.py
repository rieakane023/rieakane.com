from django.contrib import admin

from .models import AuditLog, ErrorLog


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "level", "exception_type", "status_code", "path", "resolved")
    list_filter = ("level", "resolved", "status_code")
    search_fields = ("exception_type", "message", "path")
    list_select_related = ("user",)
    readonly_fields = [f.name for f in ErrorLog._meta.fields if f.name != "resolved"]
    date_hierarchy = "timestamp"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "model", "object_id", "changed_by")
    list_filter = ("action", "model")
    search_fields = ("model", "object_id", "object_repr")
    list_select_related = ("changed_by",)
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):  # append-only
        return False

    def has_change_permission(self, request, obj=None):
        return False
