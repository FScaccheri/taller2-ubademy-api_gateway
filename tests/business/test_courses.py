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

    response = client.get('/search_courses/Programming/Silver')

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['courses'][0]['title'] == 'Course 1'
    assert response_data['courses'][0]['type'] == 'Programming'
    assert response_data['courses'][0]['subscription_type'] == 'Silver'

    mock_search_course.return_value.json.return_value = {
        'status': 'ok',
        'courses': [
            {'id': 2, 'title': 'Course 2', 'type': 'Cooking', 'subscription_type': 'Free'},
        ]
    }

    response = client.get('/search_courses/Cooking/Free')

    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert response_data['courses'][0]['title'] == 'Course 2'
    assert response_data['courses'][0]['type'] == 'Cooking'
    assert response_data['courses'][0]['subscription_type'] == 'Free'


@patch('main.requests.get')
def test_course_students(mock_course_students):
    mock_course_students.return_value = MagicMock(status_code=200)
    mock_course_students.return_value.json.return_value = {
        'status': 'ok',
        'students': [
            'student1@mail.com',
            'student2@mail.com',
            'student3@mail.com',
            'student4@mail.com'
        ]
    }

    response = client.get('/courses/1/students')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'students' in response_data
    assert len(response_data['students']) == 4


@patch('main.requests.get')
def test_course_exam_students(mock_course_exam_students):
    mock_course_exam_students.return_value = MagicMock(status_code=200)
    mock_course_exam_students.return_value.json.return_value = {
        'status': 'ok',
        'students': [
            'student2@mail.com',
            'student5@mail.com'
        ]
    }

    response = client.get('/courses/courseId12345/Primer parcial/students')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'students' in response_data
    assert len(response_data['students']) == 2


@patch('main.requests.get')
def test_course_exams(mock_course_exams):
    mock_course_exams.return_value = MagicMock(status_code=200)
    mock_course_exams.return_value.json.return_value = {
        'status': 'ok',
        'exams': [
            {'name': 'First exam', 'questions': 1},
            {'name': 'First exam', 'questions': 10},
            {'name': 'First exam', 'questions': 4},
            {'name': 'First exam', 'questions': 7},
            {'name': 'First exam', 'questions': 2},
        ]
    }

    response = client.get('/courses/1/exams')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'exams' in response_data
    assert len(response_data['exams']) == 5


@patch('main.requests.get')
def test_student_exams(mock_student_exams):
    mock_student_exams.return_value = MagicMock(status_code=200)
    mock_student_exams.return_value.json.return_value = {
        'status': 'ok',
        'exams': [
            {'name': 'First exam', 'questions': 10, 'mark': 10},
            {'name': 'First exam', 'questions': 7, 'mark': 8}
        ]
    }

    response = client.get('/courses/1/students_exams/approved')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'exams' in response_data
    assert len(response_data['exams']) == 2


@patch('main.requests.get')
def test_get_course_exam(mock_course_exam):
    mock_course_exam.return_value = MagicMock(status_code=200)
    mock_course_exam.return_value.json.return_value = {
        'status': 'ok',
        'exam': {'name': 'First exam', 'questions': 10, 'mark': 10}
    }

    response = client.get('/courses/1/students_exams/completed_exam')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'exam' in response_data


@patch('main.requests.post')
def test_course_subscription(mock_course_subscription):
    mock_course_subscription.return_value = MagicMock(status_code=200)
    mock_course_subscription.return_value.json.return_value = {'status': 'ok'}

    response = client.post('/courses/subscribe', json={
        'course_id': 'someCourseId12345',
        'user_email': 'test@mail.com'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.post')
def test_course_unsubscription(mock_course_unsubscription):
    mock_course_unsubscription.return_value = MagicMock(status_code=200)
    mock_course_unsubscription.return_value.json.return_value = {'status': 'ok'}

    response = client.post('/courses/unsubscribe', json={
        'course_id': 'someCourseId12345',
        'user_email': 'test@mail.com'
    })
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'


@patch('main.requests.get')
def test_get_passing_courses(mock_passing_courses):
    mock_passing_courses.return_value = MagicMock(status_code=200)
    mock_passing_courses.return_value.json.return_value = {
        'status': 'ok',
        'courses': [
            'Curso de Python',
            'Curso de C',
            'Curso de pasteleria',
        ]
    }

    response = client.get('/courses/passing')
    response_data = response.json()

    assert response.status_code != 400
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert 'courses' in response_data
    assert len(response_data['courses']) == 3
