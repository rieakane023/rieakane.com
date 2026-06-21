from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsAdminPanelUser(BasePermission):
    """
    Baseline gate for every admin endpoint: authenticated, active, `is_staff`,
    and holding a known role. Default-deny — the public has no access (security.md
    §3.3). Enforced server-side; the UI only reflects it.
    """

    message = "Admin access requires an active staff account with a role."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.is_staff
            and getattr(user, "role", None) in User.Role.values
        )


class IsAdminWriter(IsAdminPanelUser):
    """Read for any admin user; writes only for roles that may mutate data."""

    message = "Your role is read-only for this resource."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.can_write


class IsSuperadmin(IsAdminPanelUser):
    """High-impact actions (managing admin users) — superadmin only."""

    message = "This action requires the superadmin role."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superadmin
