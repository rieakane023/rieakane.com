import pytest
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from accounts.models import User
from audit.current_user import reset_current_user, set_current_user
from audit.exceptions import drf_exception_handler
from audit.middleware import ExceptionLoggingMiddleware, record_error
from audit.models import AuditLog, ErrorLog

pytestmark = pytest.mark.django_db


class FakeRequest:
    def __init__(self, user=None):
        self.path = "/api/boom/"
        self.method = "GET"
        self.request_id = "req-123"
        self.user = user


# ---- Audit trail ------------------------------------------------------------

def test_create_is_audited_and_password_scrubbed(make_user):
    user = User.objects.create_user(username="alice", password="secret-123", role=User.Role.EDITOR)
    entry = AuditLog.objects.get(model="accounts.User", object_id=str(user.pk))
    assert entry.action == AuditLog.Action.CREATE
    # Password must never be stored in plaintext in the audit trail.
    assert entry.changes["password"]["new"] == "********"
    assert entry.changes["role"]["new"] == User.Role.EDITOR


def test_update_records_only_changed_fields(make_user):
    user = make_user(User.Role.READONLY)
    AuditLog.objects.all().delete()  # ignore the create entry
    user.role = User.Role.ADMIN
    user.save()
    entry = AuditLog.objects.get(model="accounts.User", action=AuditLog.Action.UPDATE)
    assert entry.changes == {"role": {"old": User.Role.READONLY, "new": User.Role.ADMIN}}


def test_delete_is_audited(make_user):
    user = make_user()
    pk = user.pk
    user.delete()
    assert AuditLog.objects.filter(
        model="accounts.User", object_id=str(pk), action=AuditLog.Action.DELETE
    ).exists()


def test_changed_by_attribution(make_user):
    actor = make_user(username="actor")
    token = set_current_user(actor)
    try:
        make_user(username="created-by-actor")
    finally:
        reset_current_user(token)
    entry = AuditLog.objects.get(object_repr__startswith="created-by-actor")
    assert entry.changed_by == actor


# ---- Error logging ----------------------------------------------------------

def test_record_error_persists_fields():
    record_error(FakeRequest(), ValueError("kaboom"), status_code=500)
    log = ErrorLog.objects.latest("timestamp")
    assert log.exception_type == "ValueError"
    assert log.message == "kaboom"
    assert log.status_code == 500
    assert log.level == ErrorLog.Level.CRITICAL
    assert log.request_id == "req-123"


def test_middleware_records_server_errors():
    mw = ExceptionLoggingMiddleware(lambda r: Response())
    mw.process_exception(FakeRequest(), RuntimeError("explode"))
    assert ErrorLog.objects.filter(exception_type="RuntimeError").exists()


@pytest.mark.parametrize("exc", [Http404("nope"), PermissionDenied("forbidden")])
def test_middleware_ignores_client_errors(exc):
    """404 / 403 are ordinary responses, not server errors — never logged."""
    mw = ExceptionLoggingMiddleware(lambda r: Response())
    mw.process_exception(FakeRequest(), exc)
    assert ErrorLog.objects.count() == 0


def test_drf_handler_logs_only_5xx_and_avoids_double_logging():
    ctx = {"request": FakeRequest()}

    # 4xx validation error → handled by DRF, not logged.
    drf_exception_handler(ValidationError("bad"), ctx)
    assert ErrorLog.objects.count() == 0

    # Unhandled (DRF returns None and re-raises) → NOT logged here; the
    # middleware logs the re-raised exception once.
    assert drf_exception_handler(ValueError("uncaught"), ctx) is None
    assert ErrorLog.objects.count() == 0

    # NotFound maps to a 404 response → not a server error.
    drf_exception_handler(NotFound(), ctx)
    assert ErrorLog.objects.count() == 0
