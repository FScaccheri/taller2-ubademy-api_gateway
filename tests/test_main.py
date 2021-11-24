from fastapi.testclient import TestClient
from main import app, authenticate_token
from models.tokens import TokenData


def authenticate_token_override():
    return TokenData(email='mail@mail.com', is_admin=False)


app.dependency_overrides[authenticate_token] = authenticate_token_override


client = TestClient(app)


def test_home():
    response = client.get('/')
    assert response.status_code != 400
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'message': 'Hello API gateway!'}
