
from starlette.testclient import TestClient
from app.main import create_app

def test_live():
    client = TestClient(create_app())
    r = client.get('/health/live')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'
