from tests.test_main import client
from unittest.mock import patch, MagicMock


@patch('main.requests.post')
def test_successful_admin_login(mock_admin_login):
    mock_admin_login.return_value = MagicMock(status_code=200)
    mock_admin_login.return_value.json.return_value = {'status': 'ok'}

    response = client.post('/admin_login', json={
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
def test_failed_admin_login(mock_admin_login):
    mock_admin_login.return_value = MagicMock(status_code=200)
    mock_admin_login.return_value.json.return_value = {
        'status': 'error',
        'message': 'error_bad_login'
    }

    response = client.post('/admin_login', json={
        'email': 'non_existent_mail@mail.com',
        'password': 'non_existent_password'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert response_data['message'] == 'error_bad_login'


@patch('main.requests.post')
def test_successful_sign_up(mock_admin_sign_up):
    email = 'mail@mail.com'
    name = 'John Doe'

    mock_admin_sign_up.return_value = MagicMock(status_code=200)
    mock_admin_sign_up.return_value.json.return_value = {
        'status': 'ok',
        'email': email,
        'name': name
    }

    response = client.post('/admin_register', json={
        'email': email,
        'password': 'secret_password',
        'name': name
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.post')
def test_failed_sign_up(mock_admin_sign_up):
    email = 'mail@mail.com'
    name = 'John Doe'

    mock_admin_sign_up.return_value = MagicMock(status_code=200)
    mock_admin_sign_up.return_value.json.return_value = {'status': 'error'}

    response = client.post('/admin_register', json={
        'email': email,
        'password': 'secret_password',
        'name': name
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'


@patch('main.requests.get')
def test_get_all_users(mock_admin_all_users):
    mock_admin_all_users.return_value = MagicMock(status_code=200)
    mock_admin_all_users.return_value.json.return_value = {
        'status': 'ok',
        'users': [
            'mail_1@mail.com',
            'mail_2@mail.com',
            'mail_3@mail.com'
        ]
    }

    response = client.get('/get_all_users')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'users' in response_data
    assert len(response_data['users']) == 3
