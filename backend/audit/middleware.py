import logging
import traceback
import uuid

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404

from .current_user import reset_current_user, set_current_user

logger = logging.getLogger("audit")

# Exceptions that map to ordinary client responses (404/403), not server errors.
# These must never be recorded as ErrorLog entries.
_IGNORED_EXCEPTIONS = (Http404, PermissionDenied)


class CurrentUserMiddleware:
    """Expose request.user to audit signals via a contextvar, and tag a request id."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid.uuid4().hex
        token = set_current_user(getattr(request, "user", None))
        try:
            return self.get_response(request)
        finally:
            reset_current_user(token)


class ExceptionLoggingMiddleware:
    """
    Persist unhandled exceptions to ErrorLog so they surface in the admin
    Error-logs tab — systemwide, covering every Django view (admin, server-
    rendered, and DRF errors that DRF re-raises as uncaught).

    DRF API errors that DRF turns into a 5xx response are recorded by
    audit.exceptions.drf_exception_handler instead; when DRF leaves an exception
    uncaught it re-raises, and that single re-raised exception is recorded here —
    so each error is logged exactly once.

    Recording must never raise or change the response — fail safe.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, _IGNORED_EXCEPTIONS):
            return None  # ordinary 404/403 — not a server error
        record_error(request, exception)
        return None  # let Django produce its normal 500 response


def record_error(request, exception, status_code=500, level=None):
    """
    Best-effort write to ErrorLog. Reusable anywhere in the backend (e.g. wrap a
    risky third-party call: `except Exc as e: record_error(request, e, 502)`).
    Swallows all failures and never disturbs the original response.
    """
    from .models import ErrorLog  # local import: app registry must be ready

    if level is None:
        level = ErrorLog.Level.CRITICAL if status_code >= 500 else ErrorLog.Level.WARNING

    user = getattr(request, "user", None)
    try:
        # Own atomic block so a broken outer transaction can't silently drop the
        # log, and a failure here is isolated.
        with transaction.atomic():
            ErrorLog.objects.create(
                level=level,
                exception_type=type(exception).__name__,
                message=str(exception)[:2000],
                traceback="".join(
                    traceback.format_exception(type(exception), exception, exception.__traceback__)
                )[:10000],
                path=getattr(request, "path", "")[:512],
                method=getattr(request, "method", "")[:10],
                status_code=status_code,
                user=user if getattr(user, "is_authenticated", False) else None,
                request_id=getattr(request, "request_id", ""),
            )
    except Exception:  # noqa: BLE001 — logging must never break the request
        logger.exception("Failed to persist ErrorLog")
