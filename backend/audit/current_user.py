"""
Stash the acting user in a contextvar so audit signals (which don't see the
request) can attribute changes (django.md "Admin support"). Safe for async.
"""
from contextvars import ContextVar

_current_user: ContextVar = ContextVar("current_user", default=None)


def set_current_user(user):
    return _current_user.set(user)


def get_current_user():
    user = _current_user.get()
    if user is not None and getattr(user, "is_authenticated", False):
        return user
    return None


def reset_current_user(token):
    try:
        _current_user.reset(token)
    except (ValueError, LookupError):
        pass
