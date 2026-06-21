from django.contrib.auth import authenticate
from rest_framework import serializers

from accounts.models import User
from audit.models import AuditLog, ErrorLog


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin user management. Password is write-only; never echoed back."""

    password = serializers.CharField(write_only=True, required=False, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "role", "is_active", "is_staff", "date_joined", "last_login", "password",
        )
        read_only_fields = ("id", "date_joined", "last_login")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CurrentAdminSerializer(serializers.ModelSerializer):
    """The logged-in admin's own profile (for the UI header / role display)."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "is_superadmin")
        read_only_fields = fields


class ErrorLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ErrorLog
        fields = (
            "id", "timestamp", "level", "exception_type", "message", "traceback",
            "path", "method", "status_code", "user", "request_id", "resolved",
        )
        read_only_fields = tuple(f for f in fields if f != "resolved")


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = (
            "id", "timestamp", "action", "model", "object_id",
            "object_repr", "changes", "changed_by",
        )
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """
    MFA-ready admin login (security.md §3.2). Validates credentials, then:
      • if the user has confirmed TOTP devices, an `otp_token` is required and
        verified;
      • if settings.REQUIRE_MFA and the user has no confirmed device, login is
        refused (they must enrol first).
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    otp_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        from django.conf import settings

        request = self.context.get("request")
        user = authenticate(request, username=attrs["username"], password=attrs["password"])
        if user is None or not user.is_active:
            raise serializers.ValidationError("Invalid credentials.", code="authorization")
        if not user.is_staff:
            raise serializers.ValidationError("This account cannot access the admin.", code="authorization")

        self._verify_mfa(user, attrs.get("otp_token") or "", require=getattr(settings, "REQUIRE_MFA", False))
        attrs["user"] = user
        return attrs

    @staticmethod
    def _verify_mfa(user, token, require):
        try:
            from django_otp import devices_for_user
        except ImportError:  # django-otp not installed in this environment
            if require:
                raise serializers.ValidationError("MFA is required but unavailable.", code="mfa")
            return

        devices = list(devices_for_user(user, confirmed=True))
        if not devices:
            if require:
                raise serializers.ValidationError(
                    "MFA enrolment required before you can sign in.", code="mfa_required"
                )
            return
        if not token:
            raise serializers.ValidationError("An MFA code is required.", code="mfa_required")
        if not any(d.verify_token(token) for d in devices):
            raise serializers.ValidationError("Invalid MFA code.", code="mfa_invalid")
