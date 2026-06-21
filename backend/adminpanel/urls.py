from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserViewSet,
    AuditLogViewSet,
    ErrorLogViewSet,
    LoginView,
    LogoutView,
    MeView,
)

app_name = "adminpanel"

router = DefaultRouter()
router.register("users", AdminUserViewSet, basename="users")
router.register("error-logs", ErrorLogViewSet, basename="error-logs")
router.register("audit-logs", AuditLogViewSet, basename="audit-logs")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
