from unittest.mock import patch, MagicMock
from tests.test_main import client


@patch('main.requests.post')
def test_create_exam(mock_create_exam):
    mock_create_exam.return_value = MagicMock(status_code=200)
    mock_create_exam.return_value.json.return_value = {
        'status': 'ok',
        'message': 'Exam created successfully'
    }

    exam_data = {
        'question_1': 'Lorem impsum',
        'question_2': 'Lorem impsum',
        'question_3': 'Lorem impsum'
    }

    response = client.post('courses/create_exam', json=exam_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.post')
def test_failed_create_exam(mock_create_exam):
    mock_create_exam.return_value = MagicMock(status_code=200)
    mock_create_exam.return_value.json.return_value = {
        'status': 'error',
        'message': 'error_invalid_question'
    }

    exam_data = {
        'question_1': 25
    }

    response = client.post('courses/create_exam', json=exam_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert 'message' in response_data


@patch('main.requests.put')
def test_edit_exam(mock_edit_exam):
    mock_edit_exam.return_value = MagicMock(status_code=200)
    mock_edit_exam.return_value.json.return_value = {
        'status': 'ok',
        'message': 'Exam edited successfully'
    }

    edited_exam_data = {
        'question_1': 'Foo bar',
        'question_2': 'Foo bar',
        'question_3': 'Foo bar'
    }

    response = client.put('courses/edit_exam', json=edited_exam_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.put')
def test_failed_edit_exam(mock_edit_exam):
    mock_edit_exam.return_value = MagicMock(status_code=200)
    mock_edit_exam.return_value.json.return_value = {
        'status': 'error',
        'message': 'error_insufficient_parameters'
    }

    edited_exam_data = {
        'question_7': 'Foo bar'
    }

    response = client.put('courses/edit_exam', json=edited_exam_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert 'message' in response_data
