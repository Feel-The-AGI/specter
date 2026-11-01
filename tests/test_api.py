from fastapi.testclient import TestClient

from specter_controller.api import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_generate_plan_rejects_bad_spec():
    assert client.post("/plans/generate", json={"name": "x"}).status_code == 422
