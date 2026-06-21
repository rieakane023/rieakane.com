import pytest

pytestmark = pytest.mark.django_db


def test_health_is_public_and_ok(api_client):
    resp = api_client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.data == {"status": "ok", "service": "rieakane.com api"}
