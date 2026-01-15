from fastapi.testclient import TestClient
from main import app
import os
import pytest

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_login_fail(client):
    response = client.post("/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 200
    assert "Usuario no encontrado" in response.text or "Contraseña incorrecta" in response.text

def test_db_setup(client):
    # Verify that the DB file was created (since we are using SQLite fallback by default)
    # The app startup event should have run
    assert os.path.exists("prospectos.db")
