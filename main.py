import uvicorn
import requests

from typing import Optional
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
import os

from configuration.status_messages import public_status_messages
from models.tokens import Token, TokenData
from models.users import CurrentUser

from exceptions.expired_credentials_exception import ExpiredCredentialsException
from exceptions.invalid_credentials_exception import InvalidCredentialsException


SECRET_KEY = '944211eb42c3b243739503a1d36225a91317cffe7d1b445add87920b380ddae5'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

USERS_BACKEND_URL = os.environ.get('USERS_BACKEND_URL', 'http://0.0.0.0:8001')
BUSINESS_BACKEND_URL = os.environ.get('BUSINESS_BACKEND_URL', 'http://0.0.0.0:8002')

COURSES_PREFIX = '/courses'
PROFILES_PREFIX = '/profiles'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(_request: Request,
                                                _exc: InvalidCredentialsException):
    return JSONResponse(
        status_code=200,
        content=public_status_messages.get('invalid_credentials')
    )


@app.exception_handler(ExpiredCredentialsException)
async def expired_credentials_exception_handler(_request: Request,
                                                _exc: ExpiredCredentialsException):
    return JSONResponse(
        status_code=200,
        content=public_status_messages.get('expired_credentials')
    )


def authenticate_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        is_admin: bool = payload.get('admin') or False
        if email is None:
            raise InvalidCredentialsException()
        return TokenData(email=email, is_admin=is_admin)
    except ExpiredSignatureError:
        raise ExpiredCredentialsException()
    except JWTError:
        raise InvalidCredentialsException()


def authenticate_admin_token(token_data: TokenData = Depends(authenticate_token)):
    if not token_data.is_admin:
        raise InvalidCredentialsException()
    return TokenData


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token_data: TokenData = Depends(authenticate_token)):
    user = CurrentUser(email=token_data.email, is_admin=token_data.is_admin)
    return user


# ENDPOINTS:

@app.get('/')
async def home():
    return public_status_messages.get('hello_api_gateway')


@app.get('/users/me')
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get('/users/ping', dependencies=[Depends(authenticate_token)])
async def users_ping():
    response = requests.get(USERS_BACKEND_URL + '/pong')
    return response.json()


@app.post('/login')
# Request: https://www.starlette.io/requests/
async def login(request: Request):
    # The documentation uses data instead of json but it is not updated
    request_json = await request.json()
    response = requests.post(USERS_BACKEND_URL + request.url.path, json=request_json)
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        return public_status_messages.get('failed_authentication')

    is_biometric = request_json.get('biometric', None)
    access_token_expires = None if is_biometric else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': request_json['email']}, expires_delta=access_token_expires
    )
    token_json = Token(access_token=access_token, token_type='bearer').dict()
    return {
        **response.json(),
        **token_json
    }


@app.post('/sign_up')
async def sign_up(request: Request):
    response = requests.post(USERS_BACKEND_URL + '/create/', json=await request.json())
    response_json = response.json()
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if response_json['status'] == 'error':
        return response_json
    # Creo el perfil
    profile_json = {
        'email': response_json['email'],
    }
    profile_response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/create',
        json=profile_json
    )
    profile_response_json = profile_response.json()
    # TODO: ELIMINAR EL PERFIL EN USERS SI FALLO LA CREACION DEL PERFIL
    if profile_response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if profile_response_json['status'] == 'error':
        return profile_response_json
    # Creo el token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': response_json['email']}, expires_delta=access_token_expires
    )
    token_json = Token(access_token=access_token, token_type='bearer').dict()
    return {
        **response_json,
        **token_json
    }


# BACKOFFICE ENDPOINTS


@app.get('/admin/users_count', dependencies=[Depends(authenticate_admin_token)])
async def users_count():
    return {"status": "ok", "count": 15}


@app.post('/admin_login')
async def admin_login(request: Request):
    request_json = await request.json()
    response = requests.post(USERS_BACKEND_URL + request.url.path, json=request_json)
    response_json = response.json()
    if (response.status_code != 200 or response_json['status'] == 'error'):
        return public_status_messages.get('failed_authentication')

    access_token_data = {
        'sub': request_json['email'],
        'admin': True
    }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=access_token_data,
        expires_delta=access_token_expires
    )
    token_json = Token(access_token=access_token, token_type='bearer').dict()
    return {
        **response.json(),
        **token_json
    }


@app.post('/admin_register')
async def admin_register(request: Request, _token=Depends(authenticate_admin_token)):
    response = requests.post(USERS_BACKEND_URL + '/admin_create/', json=await request.json())
    response_json = response.json()
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if response_json['status'] == 'error':
        return response_json
    return {
        **response_json
    }


@app.get('/get_all_users')
async def get_all_users(_token=Depends(authenticate_admin_token)):
    response = requests.get(USERS_BACKEND_URL + '/users_list')
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        return public_status_messages.get('users_list_error')
    return response_json

# BUSINESS BACKEND


@app.get('/courses/ping')
async def business_ping():
    response = requests.get(BUSINESS_BACKEND_URL + '/ping')
    return response.json()


@app.get('/courses/{course_id}', dependencies=[Depends(authenticate_token)])
async def get_course(request: Request, course_id: str):
    response = requests.get(BUSINESS_BACKEND_URL + COURSES_PREFIX + f"/{course_id}")
    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")

    response_json = response.json()
    if response_json['status'] == 'error':
        return public_status_messages.get(response_json['message'])
    return response_json


@app.post('/courses/create_course')
async def create_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    response = requests.post(BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create', json=request_json)
    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")

    response_json = response.json()
    if response_json['status'] == 'error':
        return public_status_messages.get(response_json['message'])
    return response_json


@app.put('/courses/update_course')
async def update_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    response = requests.put(BUSINESS_BACKEND_URL + COURSES_PREFIX + '/update', json=request_json)

    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    response_json = response.json()
    if response_json['status'] == 'error':
        return public_status_messages.get(response_json['message'])
    return response_json


@app.post('/courses/subscribe')
async def subscribe_to_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/subscribe_to_course',
        json=request_json
    )

    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.post('/courses/unsubscribe')
async def unsubscribe_to_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/unsubscribe_from_course',
        json=request_json
    )

    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.get('/courses/{course_id}/students', dependencies=[Depends(get_current_user)])
async def course_students(course_id: str):
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/{course_id}/students'
    )
    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    response_json = response.json()
    return response_json


@app.get('/courses/{course_id}/exams', dependencies=[Depends(get_current_user)])
async def course_exams(course_id: str):
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/{course_id}/exams'
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.get('/courses/{course_id}/students_exams/{exam_filter}')
async def student_exams(course_id: str, exam_filter: str, current_user=Depends(get_current_user)):
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX +
        f'/{course_id}/students_exams/{current_user.email}/{exam_filter}'
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.get('/courses/{course_id}/exam/{exam_name}/{exam_filter}')
async def get_course_exam(
        course_id: str, exam_name: str, exam_filter: str,
        current_user=Depends(get_current_user)
):
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX +
        f'/{course_id}/exam/{current_user.email}/{exam_name}/{exam_filter}'
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.get('/search_courses/{filter_type}/{filter_value}')
async def search_courses(filter_type: str, filter_value: str):
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/organized/{filter_type}/{filter_value}'
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/courses/create_exam')
async def create_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    request_json['email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create_exam',
        json=request_json
    )
    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    response_json = response.json()
    return response_json


@app.put('/courses/edit_exam')
async def edit_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    request_json['email'] = token.email
    response = requests.put(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/edit_exam',
        json=request_json
    )
    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    response_json = response.json()
    return response_json


@app.post('/courses/publish_exam')
async def publish_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    request_json['email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/publish_exam',
        json=request_json
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.post('/courses/grade_exam')
async def grade_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    request_json['email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/grade_exam',
        json=request_json
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.post('/courses/complete_exam')
async def complete_exam(request: Request, current_user: str = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/complete_exam',
        json=request_json
    )
    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    return response_json


@app.get('/profile_setup')
async def profile_setup():
    countries_response = requests.get(BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries')
    genres_response = requests.get(BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres')

    countries_response_json = countries_response.json()
    genres_response_json = genres_response.json()
    if countries_response.status_code != 200 or genres_response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if countries_response_json['status'] == 'error':
        return public_status_messages.get('unavailable_countries')
    if genres_response_json['status'] == 'error':
        return public_status_messages.get('unavailable_genres')
    return {
        **public_status_messages.get('data_delivered'),
        'locations': countries_response_json['locations'],
        'course_genres': genres_response_json['course_genres']
    }


@app.get('/course_setup')
async def course_setup():
    # TODO: A lot of repeated code from profile_setup
    countries_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries'
    )
    genres_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres'
    )
    subscriptions_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscription_types'
    )

    countries_response_json = countries_response.json()
    genres_response_json = genres_response.json()
    subscriptions_response_json = subscriptions_response.json()
    if countries_response.status_code != 200 \
       or genres_response.status_code != 200 \
       or subscriptions_response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if countries_response_json['status'] == 'error':
        return public_status_messages.get('unavailable_countries')
    if genres_response_json['status'] == 'error':
        return public_status_messages.get('unavailable_genres')
    if subscriptions_response_json['status'] == 'error':
        return public_status_messages.get('unavailable_subscriptions')
    return {
        **public_status_messages.get('data_delivered'),
        'locations': countries_response_json['locations'],
        'course_genres': genres_response_json['course_genres'],
        'subscriptions': subscriptions_response_json['types']
    }


@app.put('/update_profile')
async def udpate_profile(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/update',
        json=request_json
    )
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        return public_status_messages.get('profile_update_error')
    return public_status_messages.get('profile_update_success')


@app.get('/profile/{profile_email}')
async def get_profile(profile_email: str, token_data=Depends(authenticate_token)):
    privilege: str = 'admin' if token_data.is_admin else 'user'
    response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + f"/{token_data.email}/{privilege}/{profile_email}"
    )
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        return public_status_messages.get('profile_get_error')

    return response_json


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
