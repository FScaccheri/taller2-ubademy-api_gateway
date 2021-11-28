from unittest.mock import patch, MagicMock
from tests.test_main import client


@patch('main.requests.get')
def test_get_profile(mock_get_profile):
    email = 'mail@mail.com'

    mock_get_profile.return_value = MagicMock(status_code=200)
    mock_get_profile.return_value.json.return_value = {
        'status': 'ok',
        'profile': {
            'id': 1,
            'name': 'John Doe',
            'email': email,
            'country': 'Argentina',
            'subscription_type': 'Gold',
            'interesting_genres': ['Physics', 'Programming']
        }
    }

    response = client.get(f'/profile/{email}')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'profile' in response_data
    assert response_data['profile']['email'] == email


@patch('main.requests.post')
def test_update_profile(mock_update_profile):
    mock_update_profile.return_value = MagicMock(status_code=200)
    mock_update_profile.return_value.json.return_value = {'status': 'ok'}

    response = client.put('/update_profile', json={
        'id': 1,
        'name': 'John Doe',
        'email': 'mail@mail.com',
        'country': 'Argentina',
        'subscription_type': 'Gold',
        'interesting_genres': ['Physics', 'Programming']
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
