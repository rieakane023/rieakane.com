"""
Generic audit trail via signals (django.md "Admin support"). Records per-field
diffs for create/update/delete on tracked models, attributing the change to the
current user (from the contextvar). Sensitive fields are scrubbed.

Tracked apps are configured by settings.AUDIT_TRACKED_APPS. The audit/error
models themselves are never tracked (avoids recursion/noise).
"""
import logging

from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .current_user import get_current_user

logger = logging.getLogger("audit")

SENSITIVE_FIELDS = {"password", "token", "secret", "key", "otp", "api_key"}
SCRUBBED = "********"
_NEVER_TRACK = {"audit.errorlog", "audit.auditlog"}


def _tracked_apps():
    return set(getattr(settings, "AUDIT_TRACKED_APPS", []))


def _is_tracked(model) -> bool:
    label = f"{model._meta.app_label}.{model._meta.model_name}"
    if label in _NEVER_TRACK:
        return False
    return model._meta.app_label in _tracked_apps()


def _serialize(value):
    try:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return str(value)
    except Exception:  # noqa: BLE001
        return "<unserializable>"


def _field_value(instance, field):
    name = field.name
    if name.lower() in SENSITIVE_FIELDS:
        return SCRUBBED
    return _serialize(getattr(instance, field.attname, None))


@receiver(pre_save)
def _capture_old(sender, instance, **kwargs):
    if not _is_tracked(sender) or instance.pk is None:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    instance._audit_old = {f.name: _field_value(old, f) for f in sender._meta.concrete_fields}


@receiver(post_save)
def _on_save(sender, instance, created, **kwargs):
    if not _is_tracked(sender):
        return
    from .models import AuditLog

    new = {f.name: _field_value(instance, f) for f in sender._meta.concrete_fields}
    if created:
        changes = {k: {"old": None, "new": v} for k, v in new.items()}
        action = AuditLog.Action.CREATE
    else:
        old = getattr(instance, "_audit_old", {})
        changes = {
            k: {"old": old.get(k), "new": new[k]} for k in new if old.get(k) != new[k]
        }
        if not changes:
            return
        action = AuditLog.Action.UPDATE

    _write(action, sender, instance, changes)


@receiver(post_delete)
def _on_delete(sender, instance, **kwargs):
    if not _is_tracked(sender):
        return
    from .models import AuditLog

    snapshot = {
        f.name: {"old": _field_value(instance, f), "new": None}
        for f in sender._meta.concrete_fields
    }
    _write(AuditLog.Action.DELETE, sender, instance, snapshot)


def _write(action, sender, instance, changes):
    try:
        from .models import AuditLog

        AuditLog.objects.create(
            action=action,
            model=f"{sender._meta.app_label}.{sender._meta.object_name}",
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            changes=changes,
            changed_by=get_current_user(),
        )
    except Exception:  # noqa: BLE001 — audit must never break the write path
        logger.exception("Failed to write AuditLog")
