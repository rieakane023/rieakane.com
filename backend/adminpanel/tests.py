import pytest
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.authtoken.models import Token

from accounts.models import User
from audit.models import AuditLog, ErrorLog

pytestmark = pytest.mark.django_db

LOGIN = "/api/v1/admin/auth/login/"
LOGOUT = "/api/v1/admin/auth/logout/"
ME = "/api/v1/admin/auth/me/"
USERS = "/api/v1/admin/users/"
ERRORS = "/api/v1/admin/error-logs/"
AUDIT = "/api/v1/admin/audit-logs/"

WRITE_ROLES = [User.Role.SUPERADMIN, User.Role.ADMIN, User.Role.EDITOR, User.Role.SUPPORT, User.Role.READONLY]

# Exact, contract-pinning messages (asserted word-for-word).
NON_FIELD = "non_field_errors"
MSG_REQUIRED = "This field is required."
MSG_INVALID_CREDS = "Invalid credentials."
MSG_NOT_ADMIN = "This account cannot access the admin."
MSG_MFA_ENROL = "MFA enrolment required before you can sign in."
MSG_MFA_REQUIRED = "An MFA code is required."
MSG_MFA_INVALID = "Invalid MFA code."
MSG_NOT_AUTH = "Authentication credentials were not provided."
MSG_SUPERADMIN_ONLY = "This action requires the superadmin role."
MSG_PWD_MIN = "Ensure this field has at least 8 characters."
MSG_DEACTIVATE_SELF = "You cannot deactivate your own account."
MSG_POST_NOT_ALLOWED = 'Method "POST" not allowed.'


def _valid_totp(device):
    code = totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits, drift=device.drift)
    return f"{code:0{device.digits}d}"


# ---- Auth: login ------------------------------------------------------------

class TestLogin:
    def test_success_returns_token_and_complete_user(self, api_client, make_user):
        user = make_user(username="rie", password="pass-w0rd-123", role=User.Role.ADMIN)
        resp = api_client.post(LOGIN, {"username": "rie", "password": "pass-w0rd-123"}, format="json")
        assert resp.status_code == 200
        # Token is random — assert structurally; assert the rest of the body exactly.
        assert isinstance(resp.data["token"], str) and len(resp.data["token"]) > 0
        assert resp.data["user"] == {
            "id": user.id,
            "username": "rie",
            "email": "rie@example.com",
            "first_name": "",
            "last_name": "",
            "role": "admin",
            "is_superadmin": False,
        }

    @pytest.mark.parametrize(
        "payload,expected",
        [
            ({"username": "rie", "password": "wrong"}, {NON_FIELD: [MSG_INVALID_CREDS]}),
            ({"username": "ghost", "password": "pass-w0rd-123"}, {NON_FIELD: [MSG_INVALID_CREDS]}),
            ({"username": "rie"}, {"password": [MSG_REQUIRED]}),
            ({"password": "pass-w0rd-123"}, {"username": [MSG_REQUIRED]}),
        ],
    )
    def test_invalid_inputs_return_exact_errors(self, api_client, make_user, payload, expected):
        make_user(username="rie", password="pass-w0rd-123")
        resp = api_client.post(LOGIN, payload, format="json")
        assert resp.status_code == 400
        assert resp.data == expected

    def test_non_staff_cannot_sign_in(self, api_client, make_user):
        make_user(username="ext", password="pass-w0rd-123", is_staff=False)
        resp = api_client.post(LOGIN, {"username": "ext", "password": "pass-w0rd-123"}, format="json")
        assert resp.status_code == 400
        assert resp.data == {NON_FIELD: [MSG_NOT_ADMIN]}

    def test_mfa_required_when_enforced_and_no_device(self, api_client, make_user, settings):
        settings.REQUIRE_MFA = True
        make_user(username="rie", password="pass-w0rd-123")
        resp = api_client.post(LOGIN, {"username": "rie", "password": "pass-w0rd-123"}, format="json")
        assert resp.status_code == 400
        assert resp.data == {NON_FIELD: [MSG_MFA_ENROL]}

    def test_login_with_valid_totp_succeeds(self, api_client, make_user):
        user = make_user(username="rie", password="pass-w0rd-123")
        device = TOTPDevice.objects.create(user=user, name="phone", confirmed=True)
        resp = api_client.post(
            LOGIN,
            {"username": "rie", "password": "pass-w0rd-123", "otp_token": _valid_totp(device)},
            format="json",
        )
        assert resp.status_code == 200
        assert isinstance(resp.data["token"], str) and len(resp.data["token"]) > 0

    @pytest.mark.parametrize(
        "otp,expected_msg",
        [("", MSG_MFA_REQUIRED), ("000000", MSG_MFA_INVALID)],
    )
    def test_login_with_device_requires_correct_totp(self, api_client, make_user, otp, expected_msg):
        user = make_user(username="rie", password="pass-w0rd-123")
        TOTPDevice.objects.create(user=user, name="phone", confirmed=True)
        resp = api_client.post(
            LOGIN, {"username": "rie", "password": "pass-w0rd-123", "otp_token": otp}, format="json"
        )
        assert resp.status_code == 400
        assert resp.data == {NON_FIELD: [expected_msg]}


# ---- Auth: me / logout ------------------------------------------------------

class TestSession:
    def test_me_returns_complete_profile(self, auth_client, make_user):
        user = make_user(User.Role.ADMIN, username="rie")
        resp = auth_client(user).get(ME)
        assert resp.status_code == 200
        assert resp.data == {
            "id": user.id,
            "username": "rie",
            "email": "rie@example.com",
            "first_name": "",
            "last_name": "",
            "role": "admin",
            "is_superadmin": False,
        }

    def test_me_requires_auth(self, api_client):
        resp = api_client.get(ME)
        assert resp.status_code == 401
        assert resp.data == {"detail": MSG_NOT_AUTH}

    def test_logout_deletes_token(self, api_client, make_user):
        user = make_user()
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        resp = api_client.post(LOGOUT)
        assert resp.status_code == 204
        assert not Token.objects.filter(user=user).exists()


# ---- Users (tab 1) ----------------------------------------------------------

class TestUsersPermissions:
    def test_anonymous_denied_with_exact_message(self, api_client):
        resp = api_client.get(USERS)
        assert resp.status_code == 401
        assert resp.data == {"detail": MSG_NOT_AUTH}

    @pytest.mark.parametrize("role", WRITE_ROLES)
    def test_any_admin_can_list(self, auth_client, make_user, role):
        assert auth_client(make_user(role)).get(USERS).status_code == 200

    @pytest.mark.parametrize("role", [r for r in WRITE_ROLES if r != User.Role.SUPERADMIN])
    def test_only_superadmin_can_create(self, auth_client, make_user, role):
        resp = auth_client(make_user(role)).post(USERS, {"username": "x", "role": "editor"}, format="json")
        assert resp.status_code == 403
        assert resp.data == {"detail": MSG_SUPERADMIN_ONLY}


class TestUsersIO:
    def test_create_persists_and_hides_password(self, auth_client, superadmin_user):
        resp = auth_client(superadmin_user).post(
            USERS,
            {"username": "newadmin", "email": "n@example.com", "role": "editor",
             "password": "pass-w0rd-123", "is_staff": True},
            format="json",
        )
        assert resp.status_code == 201
        created = User.objects.get(username="newadmin")
        # password is write-only (never echoed); id/date_joined are dynamic.
        assert "password" not in resp.data
        assert resp.data["id"] == created.id
        assert resp.data["username"] == "newadmin"
        assert resp.data["email"] == "n@example.com"
        assert resp.data["role"] == "editor"
        assert resp.data["is_active"] is True
        assert resp.data["is_staff"] is True
        assert resp.data["last_login"] is None
        assert created.check_password("pass-w0rd-123")  # hashed, not plaintext

    @pytest.mark.parametrize(
        "payload,expected",
        [
            ({"username": "x", "role": "editor", "password": "short"}, {"password": [MSG_PWD_MIN]}),
            ({"role": "editor"}, {"username": [MSG_REQUIRED]}),
        ],
    )
    def test_create_validation_returns_exact_errors(self, auth_client, superadmin_user, payload, expected):
        resp = auth_client(superadmin_user).post(USERS, payload, format="json")
        assert resp.status_code == 400
        assert resp.data == expected

    def test_update_changes_role(self, auth_client, superadmin_user, make_user):
        target = make_user(User.Role.READONLY)
        resp = auth_client(superadmin_user).patch(f"{USERS}{target.pk}/", {"role": "admin"}, format="json")
        assert resp.status_code == 200
        assert resp.data["role"] == "admin"
        target.refresh_from_db()
        assert target.role == "admin"

    def test_deactivate_is_soft_and_returns_profile(self, auth_client, superadmin_user, make_user):
        target = make_user(User.Role.SUPPORT, username="tobedisabled")
        resp = auth_client(superadmin_user).post(f"{USERS}{target.pk}/deactivate/")
        assert resp.status_code == 200
        assert resp.data == {
            "id": target.id,
            "username": "tobedisabled",
            "email": "tobedisabled@example.com",
            "first_name": "",
            "last_name": "",
            "role": "support",
            "is_superadmin": False,
        }
        target.refresh_from_db()
        assert target.is_active is False

    def test_cannot_deactivate_self_exact_message(self, auth_client, superadmin_user):
        resp = auth_client(superadmin_user).post(f"{USERS}{superadmin_user.pk}/deactivate/")
        assert resp.status_code == 400
        assert resp.data == {"detail": MSG_DEACTIVATE_SELF}
        superadmin_user.refresh_from_db()
        assert superadmin_user.is_active is True

    def test_list_is_paginated_and_searchable(self, auth_client, superadmin_user, make_user):
        make_user(username="findme-zoe")
        resp = auth_client(superadmin_user).get(USERS, {"search": "findme-zoe"})
        assert resp.status_code == 200
        assert {"count", "next", "previous", "results"} == set(resp.data.keys())
        assert resp.data["count"] == 1
        assert [u["username"] for u in resp.data["results"]] == ["findme-zoe"]


# ---- Error logs (tab 2) -----------------------------------------------------

class TestErrorLogs:
    def _make_error(self, **kwargs):
        defaults = dict(exception_type="ValueError", message="boom", status_code=500)
        defaults.update(kwargs)
        return ErrorLog.objects.create(**defaults)

    def test_requires_auth_exact_message(self, api_client):
        resp = api_client.get(ERRORS)
        assert resp.status_code == 401
        assert resp.data == {"detail": MSG_NOT_AUTH}

    @pytest.mark.parametrize("role", WRITE_ROLES)
    def test_any_admin_can_read(self, auth_client, make_user, role):
        self._make_error()
        resp = auth_client(make_user(role)).get(ERRORS)
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_resolve_toggle_input_output(self, auth_client, readonly_user):
        log = self._make_error(level=ErrorLog.Level.ERROR)
        resp = auth_client(readonly_user).patch(f"{ERRORS}{log.pk}/", {"resolved": True}, format="json")
        assert resp.status_code == 200
        # Deterministic echoed fields asserted exactly (timestamp/id are dynamic).
        assert resp.data["id"] == log.id
        assert resp.data["resolved"] is True
        assert resp.data["level"] == "error"
        assert resp.data["exception_type"] == "ValueError"
        assert resp.data["message"] == "boom"
        assert resp.data["status_code"] == 500
        log.refresh_from_db()
        assert log.resolved is True

    def test_filter_by_level(self, auth_client, readonly_user):
        self._make_error(level=ErrorLog.Level.WARNING)
        self._make_error(level=ErrorLog.Level.CRITICAL)
        resp = auth_client(readonly_user).get(ERRORS, {"level": "warning"})
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["level"] == "warning"

    def test_filter_by_resolved(self, auth_client, readonly_user):
        self._make_error(resolved=True)
        self._make_error(resolved=False)
        resp = auth_client(readonly_user).get(ERRORS, {"resolved": "false"})
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["resolved"] is False


# ---- Audit trail (tab 3) ----------------------------------------------------

class TestAuditLogs:
    def test_requires_auth_exact_message(self, api_client):
        resp = api_client.get(AUDIT)
        assert resp.status_code == 401
        assert resp.data == {"detail": MSG_NOT_AUTH}

    def test_list_and_filter_by_model(self, auth_client, superadmin_user):
        # superadmin_user creation already produced an accounts.User audit entry.
        resp = auth_client(superadmin_user).get(AUDIT, {"model": "accounts.User"})
        assert resp.status_code == 200
        assert resp.data["count"] >= 1
        assert all(r["model"] == "accounts.User" for r in resp.data["results"])

    def test_models_endpoint_lists_tracked_models(self, auth_client, superadmin_user):
        resp = auth_client(superadmin_user).get(f"{AUDIT}models/")
        assert resp.status_code == 200
        assert resp.data == ["accounts.User"]

    def test_is_read_only_exact_message(self, auth_client, superadmin_user):
        resp = auth_client(superadmin_user).post(AUDIT, {}, format="json")
        assert resp.status_code == 405
        assert resp.data == {"detail": MSG_POST_NOT_ALLOWED}

    def test_entry_exposes_field_diff(self, auth_client, superadmin_user, make_user):
        AuditLog.objects.all().delete()
        user = make_user(User.Role.READONLY)
        user.role = User.Role.ADMIN
        user.save()
        resp = auth_client(superadmin_user).get(AUDIT, {"action": "update"})
        entry = resp.data["results"][0]
        assert entry["action"] == "update"
        assert entry["model"] == "accounts.User"
        assert entry["changes"] == {"role": {"old": "readonly", "new": "admin"}}
        # The change was made outside any request, so there is no acting user.
        assert entry["changed_by"] is None
