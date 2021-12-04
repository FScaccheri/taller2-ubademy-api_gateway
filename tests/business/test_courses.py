from unittest.mock import patch, MagicMock
from tests.test_main import client


@patch('main.requests.get')
def test_courses_ping(mock_courses_ping):
    mock_courses_ping.return_value = MagicMock(status_code=200)
    mock_courses_ping.return_value.json.return_value = {'status': 'ok'}

    response = client.get('/courses/ping')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.get')
def test_get_course(mock_get_course):
    mock_get_course.return_value = MagicMock(status_code=200)
    mock_get_course.return_value.json.return_value = {
        'status': 'ok',
        'course': {
            'creator_email': 'mail@mail.com',
            'title': 'My course',
            'description': 'My very own course',
            'type': 'Programming'
        }
    }

    response = client.get('/courses/5')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'course' in response_data
    assert response_data['course']['title'] == 'My course'


@patch('main.requests.post')
def test_create_course(mock_create_course):
    mock_create_course.return_value = MagicMock(status_code=200)
    mock_create_course.return_value.json.return_value = {'status': 'ok'}

    response = client.post('/courses/create_course', json={
        'title': 'My course',
        'description': 'My very own course',
        'type': 'Programming'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.put')
def test_update_course(mock_update_course):
    mock_update_course.return_value = MagicMock(status_code=200)
    mock_update_course.return_value.json.return_value = {'status': 'ok'}

    response = client.put('/courses/update_course', json={
        'title': 'My new course',
        'description': 'My brand new course',
        'type': 'Math',
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.get')
def test_search_course(mock_search_course):
    mock_search_course.return_value = MagicMock(status_code=200)
    mock_search_course.return_value.json.return_value = {
        'status': 'ok',
        'courses': [
            {'id': 1, 'title': 'Course 1', 'type': 'Programming', 'subscription_type': 'Silver'},
        ]
    }

    response = client.get('/search_courses/type/Programming')

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['courses'][0]['title'] == 'Course 1'
    assert response_data['courses'][0]['type'] == 'Programming'

    mock_search_course.return_value.json.return_value = {
        'status': 'ok',
        'courses': [
            {'id': 2, 'title': 'Course 2', 'type': 'Cooking', 'subscription_type': 'Free'},
        ]
    }

    response = client.get('/search_courses/subscription_type/Free')

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['courses'][0]['title'] == 'Course 2'
    assert response_data['courses'][0]['subscription_type'] == 'Free'