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


@patch('main.requests.post')
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


@patch('main.requests.post')
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


@patch('main.requests.post')
def test_publish_exam(mock_publish_exam):
    mock_publish_exam.return_value = MagicMock(status_code=200)
    mock_publish_exam.return_value.json.return_value = {
        'status': 'ok',
        'message': 'exam published'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Exam name 1'
    }

    response = client.post('courses/publish_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'message' in response_data
    assert response_data['message'] == 'exam published'


@patch('main.requests.post')
def test_failed_publish_exam(mock_publish_exam):
    mock_publish_exam.return_value = MagicMock(status_code=200)
    mock_publish_exam.return_value.json.return_value = {
        'status': 'error',
        'message': 'unexpected_error'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Exam name 1'
    }

    response = client.post('courses/publish_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert 'message' in response_data
    assert response_data['message'] == 'unexpected_error'


@patch('main.requests.post')
def test_grade_exam(mock_grade_exam):
    mock_grade_exam.return_value = MagicMock(status_code=200)
    mock_grade_exam.return_value.json.return_value = {
        'status': 'ok',
        'message': 'exam graded'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Exam name 1',
        'student_email': 'student@mail.com',
        'professor_email': 'professor@mail.com',
        'mark': 6,
        'corrections': [
            'Punto A bien',
            'Punto B mal',
            'Punto C excelente'
        ]
    }

    response = client.post('courses/grade_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'message' in response_data
    assert response_data['message'] == 'exam graded'


@patch('main.requests.post')
def test_failed_grade_exam(mock_grade_exam):
    mock_grade_exam.return_value = MagicMock(status_code=200)
    mock_grade_exam.return_value.json.return_value = {
        'status': 'error',
        'message': 'non existent exam'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Non existant',
        'student_email': 'student@mail.com',
        'professor_email': 'professor@mail.com',
        'mark': 2,
        'corrections': [
            'Punto A mal',
            'Punto B mal',
            'Punto C mal'
        ]
    }

    response = client.post('courses/grade_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert 'message' in response_data
    assert response_data['message'] == 'non existent exam'


@patch('main.requests.post')
def test_complete_exam(mock_complete_exam):
    mock_complete_exam.return_value = MagicMock(status_code=200)
    mock_complete_exam.return_value.json.return_value = {
        'status': 'ok',
        'message': 'exam answered'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Exam name 1',
        'student_email': 'student@mail.com',
        'answers': [
            'Respuesta A',
            'Respuesta B',
            'Respuesta C'
        ]
    }

    response = client.post('courses/complete_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'message' in response_data
    assert response_data['message'] == 'exam answered'


@patch('main.requests.post')
def test_failed_complete_exam(mock_complete_exam):
    mock_complete_exam.return_value = MagicMock(status_code=200)
    mock_complete_exam.return_value.json.return_value = {
        'status': 'error',
        'message': 'wrong answers amount'
    }

    request_data = {
        'course_id': '123456789',
        'exam_name': 'Non existant',
        'student_email': 'student@mail.com',
        'answers': [
            'Respuesta C'
        ]
    }

    response = client.post('courses/complete_exam', json=request_data)
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'error'
    assert 'message' in response_data
    assert response_data['message'] == 'wrong answers amount'


@patch('main.requests.get')
def test_get_student_exam(mock_student_exam):
    mock_student_exam.return_value = MagicMock(status_code=200)
    mock_student_exam.return_value.json.return_value = {
        'status': 'ok',
        'exam': {'name': 'First exam', 'questions': 10, 'mark': 10}
    }

    response = client.get('/courses/courseId12345/exam/First exam/completed_exam/student@mail.com')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'exam' in response_data
