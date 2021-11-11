from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get('/')
    assert response.status_code != 400
    assert response.status_code == 200
    assert response.json() == {'status':'ok','message': 'Hello API gateway!'}
