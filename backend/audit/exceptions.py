from rest_framework.views import exception_handler as drf_default_handler

from .middleware import record_error


def drf_exception_handler(exc, context):
    """
    DRF EXCEPTION_HANDLER. Records server errors (5xx) that DRF turns into a
    response, then defers to DRF's default handling.

    Expected client errors (4xx: validation, auth, permission, throttling) are
    NOT errors and are not logged. When DRF can't handle an exception it returns
    None and re-raises; we deliberately do NOT log here in that case — the
    re-raised exception reaches ExceptionLoggingMiddleware, which records it
    once. This keeps every error logged exactly once.
    """
    response = drf_default_handler(exc, context)
    request = context.get("request")

    if response is not None and response.status_code >= 500 and request is not None:
        record_error(request, exc, status_code=response.status_code)

    return response
