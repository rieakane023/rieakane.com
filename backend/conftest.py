"""
Project-wide pytest fixtures (django.md §17). Tests use `@pytest.mark.django_db`
and real objects via factories — we never mock our own code, only third-party
boundaries. Shared client/user fixtures live here so individual tests stay short.
"""
import pytest
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    """Create a real admin user of any role (db-backed, no mocking)."""

    def _make(role=User.Role.READONLY, **kwargs):
        kwargs.setdefault("is_superuser", role == User.Role.SUPERADMIN)
        return UserFactory(role=role, **kwargs)

    return _make


@pytest.fixture
def auth_client(api_client):
    """Return a callable that authenticates the shared client as a given user."""

    def _auth(user):
        api_client.force_authenticate(user=user)
        return api_client

    return _auth


# Convenience per-role users.
@pytest.fixture
def readonly_user(make_user):
    return make_user(User.Role.READONLY)


@pytest.fixture
def support_user(make_user):
    return make_user(User.Role.SUPPORT)


@pytest.fixture
def editor_user(make_user):
    return make_user(User.Role.EDITOR)


@pytest.fixture
def admin_user(make_user):
    return make_user(User.Role.ADMIN)


@pytest.fixture
def superadmin_user(make_user):
    return make_user(User.Role.SUPERADMIN)
