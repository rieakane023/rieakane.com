from django.conf import settings
from django.db import models


class ErrorLog(models.Model):
    """
    Every unhandled error is recorded here so the admin's Error logs tab works
    without SSH'ing into log files (admin.md tab 2 / django.md "Admin support").
    Writes must never raise — see audit.exceptions / audit.middleware.
    """

    class Level(models.TextChoices):
        ERROR = "error", "Error"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.ERROR)
    exception_type = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    traceback = models.TextField(blank=True)
    path = models.CharField(max_length=512, blank=True)
    method = models.CharField(max_length=10, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="error_logs",
    )
    request_id = models.CharField(max_length=64, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["resolved", "-timestamp"]),
            models.Index(fields=["exception_type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.level}] {self.exception_type}: {self.message[:60]}"


class AuditLog(models.Model):
    """
    One row per create/update/delete on a tracked model, with a per-field diff,
    so the admin's Audit trail tab can show name / old / new / changed-by /
    changed-on per model (admin.md tab 3). Append-only.
    """

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=Action.choices)
    model = models.CharField(max_length=255)  # "app_label.ModelName"
    object_id = models.CharField(max_length=64, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    # {field: {"old": ..., "new": ...}} — sensitive fields scrubbed.
    changes = models.JSONField(default=dict, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["model", "-timestamp"]),
            models.Index(fields=["-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.model}#{self.object_id} @ {self.timestamp:%Y-%m-%d %H:%M}"
