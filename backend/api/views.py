from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])  # public liveness check (overrides default-deny)
def health(request):
    """Simple liveness check for the frontend and uptime monitors."""
    return Response({"status": "ok", "service": "rieakane.com api"})
