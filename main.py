import os
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

from configuration.status_messages import public_status_messages
from models.tokens import Token, TokenData
from models.users import CurrentUser

from exceptions.expired_credentials_exception import ExpiredCredentialsException
from exceptions.invalid_credentials_exception import InvalidCredentialsException

from utils.logger import Logger

SECRET_KEY = '944211eb42c3b243739503a1d36225a91317cffe7d1b445add87920b380ddae5'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

USERS_API_KEY = os.environ.get(
    'USERS_API_KEY',
    'db927b6105712695971a38fa593db084d95f86f68a1f85030ff5326d7a30c673'
)
BUSINESS_API_KEY = os.environ.get(
    'BUSINESS_API_KEY',
    'faf5b8b0651b9baf0919f77f5b50f9b872b3521f922c14c0ad12f696b50c1b73'
)
PAYMENTS_API_KEY = os.environ.get(
    'PAYMENTS_API_KEY',
    '03aaeb781af46e2f06a9784c2a8e4b26a3fd89f96ad08e2988917ba76f7d9933'
)

USERS_BACKEND_URL = os.environ.get('USERS_BACKEND_URL', 'http://0.0.0.0:8001')
BUSINESS_BACKEND_URL = os.environ.get('BUSINESS_BACKEND_URL', 'http://0.0.0.0:8002')
PAYMENTS_BACKEND_URL = os.environ.get('PAYMENTS_BACKEND_URL', 'http://0.0.0.0:8003')
GOOGLE_OAUTH_URL = 'https://www.googleapis.com/oauth2/v3'

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

logger = Logger(os.environ.get('NEWRELIC_API_KEY'))


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(request: Request,
                                                _exc: InvalidCredentialsException):
    logger.info(f"{request.method} at {request.url.path}: invalid credentials exception")
    return JSONResponse(
        status_code=200,
        content=public_status_messages.get('invalid_credentials')
    )


@app.exception_handler(ExpiredCredentialsException)
async def expired_credentials_exception_handler(request: Request,
                                                _exc: ExpiredCredentialsException):
    logger.info(f"{request.method} at {request.url.path}: expired credentials exception")
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
    logger.info("GET request received at '/'")
    return public_status_messages.get('hello_api_gateway')


@app.get('/users/me')
async def read_users_me(current_user: dict = Depends(get_current_user)):
    logger.info("GET request received at '/users/me'")
    return current_user


@app.get('/users/ping', dependencies=[Depends(authenticate_token)])
async def users_ping():
    logger.info("GET request received at '/users/ping'")
    response = requests.get(
        USERS_BACKEND_URL + '/pong',
        headers={'Authorization': USERS_API_KEY}
    )
    return response.json()


@app.post('/login')
# Request: https://www.starlette.io/requests/
async def login(request: Request):
    # The documentation uses data instead of json but it is not updated
    request_json = await request.json()
    logger.info(f"POST request received at /login with email: {request_json['email']}")
    response = requests.post(
        USERS_BACKEND_URL + request.url.path,
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + request.url.path}"
        )
        return public_status_messages.get('error_unexpected')

    response_json = response.json()
    if response_json['status'] == 'error':
        return response_json

    validate_sub_response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + "/validate_subscription",
        json={"email": request_json["email"]},
        headers={'Authorization': BUSINESS_API_KEY}
    )

    # Ver si tiene sentido chequear error aca.
    # porque si ya llego aca en teoria el usuario se logeo bien
    if validate_sub_response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/validate_subscription'}"
        )
        return public_status_messages.get('error_unexpected')
    validate_sub_response_json = validate_sub_response.json()
    if validate_sub_response_json['status'] == 'error':
        return validate_sub_response_json

    logger.info(f"POST at /login validate_sub_response: {validate_sub_response_json}")

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
    request_json = await request.json()
    logger.info(f"POST request received at /sign_up with email: {request_json['email']}")
    logger.debug(request_json)
    response = requests.post(
        USERS_BACKEND_URL + '/create/',
        json=await request.json(),
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + '/create/'}"
        )
        return public_status_messages.get('error_unexpected')
    response_json = response.json()
    if response_json['status'] == 'error':
        return response_json
    # Creo el perfil
    profile_json = {
        'email': response_json['email'],
    }
    profile_response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/create',
        json=profile_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    # TODO: ELIMINAR EL PERFIL EN USERS SI FALLO LA CREACION DEL PERFIL
    if profile_response.status_code != 200:
        logger.error(
            f"Error making POST request at {BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/create'}"
        )
        return public_status_messages.get('error_unexpected')
    profile_response_json = profile_response.json()
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


@app.post('/oauth_login')
async def oauth_login(request: Request):
    request_json = await request.json()
    request_email = request_json['email']
    logger.info(f"POST request received at /oauth_login with email: {request_email}")
    access_token = request_json['accessToken']
    google_response = requests.get(GOOGLE_OAUTH_URL + f'/tokeninfo?access_token={access_token}')
    if google_response.status_code != 200:
        logger.error("Error requesting user data from google")
        return public_status_messages.get('error_unexpected')

    google_response_json = google_response.json()
    google_response_email = google_response_json['email']
    if not google_response_json['email_verified'] or request_email != google_response_email:
        return public_status_messages.get('unverified_google_user')

    users_response = requests.post(
        USERS_BACKEND_URL + '/oauth_login',
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )
    if users_response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + '/oauth_login'}")
        return public_status_messages.get('error_unexpected')
    users_response_json = users_response.json()

    if users_response_json['status'] == 'ok' and users_response_json['created']:
        profile_json = {
            'email': request_email,
        }
        profile_response = requests.post(
            BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/create',
            json=profile_json,
            headers={'Authorization': BUSINESS_API_KEY}
        )
        if profile_response.status_code != 200:
            logger.error(
                f"Error making POST request at {BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/create'}"
            )
            return public_status_messages.get('error_unexpected')

    # Creo el token
    access_token_expires = timedelta(minutes=OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': request_email}, expires_delta=access_token_expires
    )
    token_json = Token(access_token=access_token, token_type='bearer').dict()
    return {
        **users_response_json,
        **token_json
    }


# BACKOFFICE ENDPOINTS


@app.get('/admin/users_count', dependencies=[Depends(authenticate_admin_token)])
async def users_count():
    return {"status": "ok", "count": 15}


@app.post('/admin_login')
async def admin_login(request: Request):
    request_json = await request.json()
    logger.info(f"Received POST request at /admin_login with email: {request_json['email']}")
    response = requests.post(
        USERS_BACKEND_URL + request.url.path,
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + request.url.path}"
        )
        return public_status_messages.get('error_unexpected')
    response_json = response.json()

    if response_json['status'] == 'error':
        return response_json

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
    request_json = await request.json()
    logger.info(f"Received POST request at /admin_register with email: {request_json['email']}")
    response = requests.post(
        USERS_BACKEND_URL + '/admin_create/',
        json=await request.json(),
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + '/admin_create/'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/get_all_users')
async def get_all_users(current_user: dict = Depends(get_current_user)):
    logger.info("Received GET request at /get_all_users")
    is_admin = "false"
    if current_user.is_admin:
        is_admin = "true"
    response = requests.get(
        USERS_BACKEND_URL + f'/users_list{is_admin}',
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making GET request at {USERS_BACKEND_URL + '/users_list/' + is_admin}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()

# BUSINESS BACKEND


@app.get('/courses/ping')
async def business_ping():
    logger.info("Received GET request at /courses/ping")
    response = requests.get(
        BUSINESS_BACKEND_URL + '/ping',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    return response.json()


@app.get('/courses/data/{course_id}')
async def get_course(request: Request, course_id: str, token_data=Depends(authenticate_token)):
    logger.info(f"Received GET request at /courses/data/{course_id}")
    # TODO: Agregar el current_user.email al final del url como url param
    privilege: str = 'admin' if token_data.is_admin else 'user'
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX + \
        f"/data/{course_id}/{token_data.email}/{privilege}"
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get("error_unexpected")

    return response.json()


@app.post('/courses/create_course')
async def create_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/create_course with body {request_json}")
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create'}"
        )
        return public_status_messages.get("error_unexpected")

    return response.json()


@app.put('/courses/update_course')
async def update_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received PUT request at /courses/create_course with body {request_json}")
    request_json['email'] = current_user.email
    response = requests.put(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/update',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )

    if response.status_code != 200:
        logger.error(
            f"Error making PUT request at {BUSINESS_BACKEND_URL + COURSES_PREFIX + '/update'}"
        )
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.post('/courses/subscribe')
async def subscribe_to_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/subscribe with body {request_json}")
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscribe_to_course',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )

    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscribe_to_course'}"
        )
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.post('/courses/unsubscribe')
async def unsubscribe_to_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/unsubscribe with body {request_json}")
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/unsubscribe_from_course',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )

    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/unsubscribe_from_course'}"
        )
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.get('/courses/{course_id}/students', dependencies=[Depends(get_current_user)])
async def course_students(course_id: str):
    logger.info(f"Received GET request at /courses/{course_id}/students")
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/{course_id}/students',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making GET request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/' + course_id + '/students'}"
        )
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.get('/courses/{course_id}/{exam_name}/students')
async def course_exam_students(course_id: str,
                               exam_name: str,
                               current_user=Depends(get_current_user)):
    logger.info(f"Received GET request at /courses/{course_id}/{exam_name}/students")

    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX + \
        f'/{course_id}/students/{current_user.email}/{exam_name}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.get('/courses/{course_id}/exams/{exam_filter}')
async def course_exams(course_id: str, exam_filter: str, current_user=Depends(get_current_user)):
    logger.info(f"Received GET request at /courses/{course_id}/exams/{filter}")
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX \
        + f'/exams/{course_id}/{exam_filter}/{current_user.email}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/courses/{course_id}/students_exams/{exam_filter}')
async def student_exams(course_id: str, exam_filter: str, current_user=Depends(get_current_user)):
    logger.info(f"Received GET request at /courses/{course_id}/students_exams/{exam_filter}")
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX \
        + f'/{course_id}/students_exams/{current_user.email}/{exam_filter}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/courses/{course_id}/exam/{exam_name}/{exam_filter}/{student_email}')
async def get_course_exam(
        course_id: str, exam_name: str, exam_filter: str, student_email: str,
        current_user=Depends(get_current_user)
):
    logger.info(f"Received GET request at "
                f"/courses/{course_id}/exam/{exam_name}/{exam_filter}/{student_email}")
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX + \
        f'/{course_id}/exam/{current_user.email}/{exam_name}/{exam_filter}/{student_email}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/search_courses/{course_type}/{subscription_type}')
async def search_courses(course_type: str,
                         subscription_type: str,
                         current_user: str = Depends(get_current_user)):
    logger.info(f"Received GET request at /search_courses/{course_type}/{subscription_type}")
    is_admin_string = "false"
    if (current_user.is_admin):
        is_admin_string = "true"
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX + \
        f'/organized/{course_type}/{subscription_type}/{is_admin_string}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/courses/create_exam')
async def create_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/create_exam with body {request_json}")
    request_json['exam_creator_email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create_exam',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making POST request at "
                     f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/create_exam'}")
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.put('/courses/edit_exam')
async def edit_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    logger.info(f"Received PUT request at /courses/edit_exam with body {request_json}")
    request_json['email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/edit_exam',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error("fError making POST request at "
                     f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/edit_exam'}")
        return public_status_messages.get("error_unexpected")
    return response.json()


@app.post('/courses/publish_exam')
async def publish_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/publish_exam with body {request_json}")
    request_json['exam_creator_email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/publish_exam',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/publish_exam'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/courses/grade_exam')
async def grade_exam(request: Request, token: str = Depends(authenticate_token)):
    request_json = await request.json()
    logger.info(f"Received POST request at /course/grade_exam with body {request_json}")
    request_json['professor_email'] = token.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/grade_exam',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/grade_exam'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/courses/complete_exam')
async def complete_exam(request: Request, current_user: str = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/compelte_exam with body {request_json}")
    request_json['student_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/complete_exam',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/complete_exam'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/courses/add_collaborator')
async def add_collaborator(request: Request, current_user: str = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /courses/add_collaborator with body {request_json}")
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/add_collaborator',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/add_collaborator'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/profile_setup')
async def profile_setup():
    logger.info("Received GET request at /profile_setup")
    countries_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    genres_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if countries_response.status_code != 200 or genres_response.status_code != 200:
        logger.error(f"Error making GET request at "
                     f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries'} or "
                     f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres'}")
        return public_status_messages.get('error_unexpected')

    countries_response_json = countries_response.json()
    genres_response_json = genres_response.json()
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
    logger.info("Received GET request at /course_setup")
    # TODO: A lot of repeated code from profile_setup
    countries_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    genres_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    subscriptions_response = requests.get(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscription_types',
        headers={'Authorization': BUSINESS_API_KEY}
    )

    if countries_response.status_code != 200 \
       or genres_response.status_code != 200 \
       or subscriptions_response.status_code != 200:
        logger.error(f"Error making GET request at "
                     f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/countries'}, "
                     f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres'} or"
                     f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscription_types'}")
        return public_status_messages.get('error_unexpected')

    countries_response_json = countries_response.json()
    genres_response_json = genres_response.json()
    subscriptions_response_json = subscriptions_response.json()

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
async def update_profile(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received PUT request at /update_profile with body {request_json}")
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/update',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )

    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/update'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/profile/{profile_email}')
async def get_profile(profile_email: str, token_data=Depends(authenticate_token)):
    logger.info(f"Received GET request at /profile/{profile_email}")
    privilege: str = 'admin' if token_data.is_admin else 'user'

    request_url = BUSINESS_BACKEND_URL + PROFILES_PREFIX + \
        f"/{token_data.email}/{privilege}/{profile_email}"
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')

    return response.json()


# SUBSCRIPTION ENDPOINTS
@app.post('/modify_subscription')
async def modify_subscription(request: Request, current_user: dict = Depends(get_current_user)):
    # Should have the new subscription wanted(Silver, Gold, Platinum)
    request_json = await request.json()
    logger.info(f"Received POST request at /modify_subscription with body {request_json}")
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/modify_subscription',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/modify_subscription'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/pay_subscription')
async def pay_subscription(request: Request, current_user: dict = Depends(get_current_user)):
    # Should have the new subscription wanted(Silver, Gold, Platinum)
    request_json = await request.json()
    logger.info(f"Received POST request at /pay_subscription with body {request_json}")
    request_json['email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/pay_subscription',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/pay_subscription'}"
        )
        return {"status": "error", "message": response_json["message"]}
    return response_json


# El email es para el filtro. Si es all devuelve todas las transacciones
@app.get('/deposits/{email}', dependencies=[Depends(authenticate_admin_token)])
async def get_deposits(request: Request, email: str):
    logger.info(f'Received GET request at /deposits/{email}')
    response = requests.get(
        PAYMENTS_BACKEND_URL + f"/deposits/{email}",
        headers={'Authorization': PAYMENTS_API_KEY}
    )
    if response.status_code != 200:
        logger.info(f'Error making GET request at {PAYMENTS_BACKEND_URL}/deposits/{email}')
        return public_status_messages.get("error_unexpected")

    return response.json()


@app.get('/my_courses')
async def my_courses(request: Request, current_user: dict = Depends(get_current_user)):
    logger.info("Received GET request at /my_courses")

    request_url = BUSINESS_BACKEND_URL + PROFILES_PREFIX + \
        f'/my_courses/{current_user.email}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/course_genres')
async def course_genres(request: Request, current_user: dict = Depends(get_current_user)):
    logger.info("Received GET request at /course_genres")

    request_url = BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/course_genres'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/subscription_types')
async def subscription_types(request: Request, current_user: dict = Depends(get_current_user)):
    logger.info("Received GET request at /subscription_types")

    request_url = BUSINESS_BACKEND_URL + PROFILES_PREFIX + '/subscription_types_names'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/courses/passing')
async def get_passing_courses(current_user=Depends(get_current_user)):
    logger.info("Received GET request at /courses/passing")
    request_url = BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/passing_courses/{current_user.email}'
    response = requests.get(
        request_url,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(f"Error making GET request at {request_url}")
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/change_blocked_status', dependencies=[Depends(authenticate_token)])
async def change_blocked_status(request: Request):
    # Should have the new subscription wanted(Silver, Gold, Platinum)
    request_json = await request.json()
    logger.info(f"Received POST request at /change_blocked_status with body {request_json}")
    response = requests.post(
        USERS_BACKEND_URL + '/change_blocked_status',
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )
    response_json = response.json()
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at {USERS_BACKEND_URL + '/change_blocked_status'}"
        )
        return public_status_messages.get('error_unexpected')
    return response_json


@app.post('/grade_course')
async def grade_course(request: Request, current_user=Depends(get_current_user)):
    request_json = await request.json()
    logger.info(f"Received POST request at /grade_course with body {request_json}")
    request_json['user_email'] = current_user.email
    response = requests.post(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + '/grade_course',
        json=request_json,
        headers={'Authorization': BUSINESS_API_KEY}
    )
    response_json = response.json()
    if response.status_code != 200:
        logger.error(
            f"Error making POST request at "
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/grade_course'}"
        )
        return public_status_messages.get('error_unexpected')
    return response_json


@app.get('/student_gradings/{student_id}', dependencies=[Depends(authenticate_token)])
async def get_student_gradings(student_id: str):
    logger.info(f"Received GET request at /student_gradings{student_id}")
    response = requests.get(
        BUSINESS_BACKEND_URL + COURSES_PREFIX + f'/student_gradings/{student_id}',
        headers={'Authorization': BUSINESS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making GET request at"
            f"{BUSINESS_BACKEND_URL + COURSES_PREFIX + '/student_gradings/' + student_id}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.get('/users_metrics', dependencies=[Depends(authenticate_admin_token)])
async def users_metrics():
    logger.info("Received GET request at /users_metrics")
    response = requests.get(
        USERS_BACKEND_URL + '/users_metrics',
        headers={'Authorization': USERS_API_KEY}
    )
    if response.status_code != 200:
        logger.error(
            f"Error making GET request at {USERS_BACKEND_URL + '/users_metrics'}"
        )
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/send_message')
async def send_message(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    logger.info(f"Received POST request at /send_message with body {request_json}")

    response = requests.post(
        USERS_BACKEND_URL + '/send_message',
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )

    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    return response.json()


@app.post('/logout')
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = {'email': current_user.email}
    logger.info(f"Received POST request at /logout with body {request_json}")

    response = requests.post(
        USERS_BACKEND_URL + '/log_out',
        json=request_json,
        headers={'Authorization': USERS_API_KEY}
    )

    if response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    return response.json()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
