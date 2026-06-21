import pytest

from accounts.models import User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "role,expected_write",
    [
        (User.Role.SUPERADMIN, True),
        (User.Role.ADMIN, True),
        (User.Role.EDITOR, True),
        (User.Role.SUPPORT, False),
        (User.Role.READONLY, False),
    ],
)
def test_can_write_per_role(make_user, role, expected_write):
    assert make_user(role).can_write is expected_write


@pytest.mark.parametrize(
    "role,expected",
    [(User.Role.SUPERADMIN, True), (User.Role.ADMIN, False), (User.Role.READONLY, False)],
)
def test_is_superadmin_predicate(make_user, role, expected):
    assert make_user(role).is_superadmin is expected


def test_role_defaults_to_readonly(make_user):
    assert make_user().role == User.Role.READONLY


def test_str_includes_username_and_role(make_user):
    user = make_user(User.Role.ADMIN, username="rie")
    assert str(user) == "rie (admin)"
