"""Pruebas de integración. Ejecutar con el stack Docker levantado."""
import os

import httpx

BASE = os.getenv("LAB_URL", "http://localhost:8000")
BACKEND = os.getenv("BACKEND_TEST_URL", "http://localhost:9000")


def test_backend_no_se_puede_saltar_gateway():
    response = httpx.get(f"{BACKEND}/products", timeout=10)
    assert response.status_code == 403


def test_login_incorrecto():
    response = httpx.post(f"{BASE}/auth/login", json={"username": "ana", "password": "mal"}, timeout=10)
    assert response.status_code == 401


def test_ana_usuario_y_logout():
    with httpx.Client(base_url=BASE, timeout=10) as client:
        assert client.get("/auth/me").status_code == 401
        result = client.post("/auth/login", json={"username": "ana", "password": "1234"})
        assert result.status_code == 200
        assert "httponly" in result.headers["set-cookie"].lower()
        assert "access_token" not in result.json()
        me = client.get("/auth/me")
        assert me.status_code == 200
        assert me.json()["roles"] == ["user"]
        assert client.get("/api/products").status_code == 200
        assert client.get("/api/orders").status_code == 200
        assert client.delete("/api/products/1").status_code == 403
        assert client.post("/auth/logout").status_code == 200
        assert client.get("/auth/me").status_code == 401


def test_admin_puede_eliminar():
    with httpx.Client(base_url=BASE, timeout=10) as client:
        response = client.post("/auth/login", json={"username": "ernesto", "password": "admin123"})
        assert response.status_code == 200
        response = client.delete("/api/products/1")
        assert response.status_code == 200
        assert response.json()["deleted"]["id"] == 1
