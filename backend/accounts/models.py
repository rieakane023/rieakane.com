from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model (set as AUTH_USER_MODEL from the first migration, per
    django.md §11). Adds a `role` for least-privilege admin access; role checks
    are enforced server-side in adminpanel.permissions.

    Admin-panel reachability is gated on `is_staff` AND an active role; the
    public site has no user-facing accounts yet, but this model is ready for them.
    """

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Superadmin"
        ADMIN = "admin", "Admin"
        EDITOR = "editor", "Editor"
        SUPPORT = "support", "Support"
        READONLY = "readonly", "Read-only"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READONLY,
        help_text="Admin privilege level. Enforced server-side, never trust the UI.",
    )

    class Meta:
        ordering = ["username"]
        indexes = [models.Index(fields=["role"])]

    def __str__(self) -> str:
        return f"{self.get_username()} ({self.role})"

    # Convenience role predicates (used by permissions / serializers).
    @property
    def is_superadmin(self) -> bool:
        return self.role == self.Role.SUPERADMIN

    @property
    def can_write(self) -> bool:
        """Roles allowed to mutate data in the admin."""
        return self.role in {self.Role.SUPERADMIN, self.Role.ADMIN, self.Role.EDITOR}
