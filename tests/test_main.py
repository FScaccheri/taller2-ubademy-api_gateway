from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get('/')
    assert response.status_code != 400
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'message': 'Hello API gateway!'}


@patch('main.requests.post')
def test_successful_login(mock_users_login):
    mock_users_login.return_value = MagicMock(status_code=200)
    mock_users_login.return_value.json.return_value = {'status': 'ok'}

    response = client.post('/login', json={
        'email': 'mail@mail.com',
        'password': 'secret_password'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'bearer'


@patch('main.requests.post')
def test_failed_login(mock_users_login):
    mock_users_login.return_value = MagicMock(status_code=200)
    mock_users_login.return_value.json.return_value = {'status': 'error'}

    response = client.post('/login', json={
        'email': 'non_existent_mail@mail.com',
        'password': 'non_existent_password'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert response_data['message'] == 'error_bad_login'


@patch('main.requests.post')
def test_successful_sign_up(mock_users_sign_up):
    email = 'mail@mail.com'
    name = 'John Doe'

    mock_users_sign_up.return_value = MagicMock(status_code=200)
    mock_users_sign_up.return_value.json.return_value = {
        'status': 'ok',
        'email': email,
        'name': name
    }

    response = client.post('/sign_up', json={
        'email': email,
        'password': 'secret_password',
        'name': name
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.post')
def test_failed_sign_up(mock_users_sign_up):
    email = 'mail@mail.com'
    name = 'John Doe'

    mock_users_sign_up.return_value = MagicMock(status_code=200)
    mock_users_sign_up.return_value.json.return_value = {'status': 'error'}

    response = client.post('/sign_up', json={
        'email': email,
        'password': 'secret_password',
        'name': name
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
