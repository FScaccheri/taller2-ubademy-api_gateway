from tests.test_main import client
from unittest.mock import patch, MagicMock


@patch('main.requests.get')
def test_users_ping(mock_users_ping):
    mock_users_ping.return_value = MagicMock(status_code=200)
    mock_users_ping.return_value.json.return_value = {'status': 'ok'}

    response = client.get('/users/ping')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


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
@patch('main.requests.get')
def test_oauth_login(mock_google_oauth, mock_oauth_login):
    email = 'test_email@mail.com'
    mock_google_oauth.return_value = MagicMock(status_code=200)
    mock_google_oauth.return_value.json.return_value = {
        'email_verified': True,
        'email': email
    }
    mock_oauth_login.return_value = MagicMock(status_code=200)
    mock_oauth_login.return_value.json.return_value = {
        'status': 'ok',
        'created': False
    }

    response = client.post('/oauth_login', json={
        'email': email,
        'accessToken': '123456789Token987654321'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'bearer'
    assert 'created' in response_data
    assert not response_data['created']


@patch('main.requests.post')
@patch('main.requests.get')
def test_oauth_login_with_non_existent_user(mock_google_oauth, mock_oauth_login):
    email = 'test_email@mail.com'
    mock_google_oauth.return_value = MagicMock(status_code=200)
    mock_google_oauth.return_value.json.return_value = {
        'email_verified': True,
        'email': email
    }
    mock_oauth_login.return_value = MagicMock(status_code=200)
    mock_oauth_login.return_value.json.return_value = {
        'status': 'ok',
        'created': True
    }

    response = client.post('/oauth_login', json={
        'email': email,
        'accessToken': '123456789Token987654321'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'bearer'
    assert 'created' in response_data
    assert response_data['created']


@patch('main.requests.get')
def test_failed_oauth_login(mock_google_oauth):
    mock_google_oauth.return_value = MagicMock(status_code=400)

    response = client.post('/oauth_login', json={
        'email': 'test_email@mail,com',
        'accessToken': '123456789Token987654321'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert response_data['message'] == 'error_unexpected'


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
