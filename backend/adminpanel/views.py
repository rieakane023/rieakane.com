from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from audit.models import AuditLog, ErrorLog

from .pagination import AdminPagination
from .permissions import IsAdminPanelUser, IsSuperadmin
from .serializers import (
    AdminUserSerializer,
    AuditLogSerializer,
    CurrentAdminSerializer,
    ErrorLogSerializer,
    LoginSerializer,
)

User = get_user_model()


class LoginView(APIView):
    """Issue an admin API token after credential + MFA checks. Rate-limited."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": CurrentAdminSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Invalidate the caller's API token."""

    permission_classes = [IsAdminPanelUser]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Current admin profile (role display in the UI)."""

    permission_classes = [IsAdminPanelUser]

    def get(self, request):
        return Response(CurrentAdminSerializer(request.user).data)


class AdminUserViewSet(viewsets.ModelViewSet):
    """Tab 1 — User management. Superadmin-only for writes (admin.md §4)."""

    queryset = User.objects.all().order_by("username")
    serializer_class = AdminUserSerializer
    permission_classes = [IsSuperadmin]
    pagination_class = AdminPagination
    filterset_fields = ["role", "is_active", "is_staff"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined", "last_login", "role"]

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Soft-disable an admin account (reversible) instead of deleting."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(CurrentAdminSerializer(user).data)


class ErrorLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Tab 2 — Error logs. Read + toggle `resolved`; never created via API."""

    queryset = ErrorLog.objects.select_related("user").all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAdminPanelUser]
    pagination_class = AdminPagination
    filterset_fields = ["level", "resolved", "status_code"]
    search_fields = ["exception_type", "message", "path"]
    ordering_fields = ["timestamp", "level", "status_code"]


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Tab 3 — Audit trail. Read-only, filterable per model (admin.md §3)."""

    queryset = AuditLog.objects.select_related("changed_by").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminPanelUser]
    pagination_class = AdminPagination
    filterset_fields = ["model", "action"]
    search_fields = ["model", "object_id", "object_repr"]
    ordering_fields = ["timestamp", "model", "action"]

    @action(detail=False, methods=["get"])
    def models(self, request):
        """Distinct tracked models, to populate the per-model tab selector."""
        names = AuditLog.objects.values_list("model", flat=True).distinct().order_by("model")
        return Response(list(names))
