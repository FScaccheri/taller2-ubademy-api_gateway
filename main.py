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
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
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
    if (response.status_code != 200 or response_json['status'] == 'error'):
        return public_status_messages.get('failed_authentication')

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    if response.status_code != 200 or response_json['status'] == 'error':
        return public_status_messages.get('failed_sign_up')
    # Creo el token
    user = response_json['user']
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['email']}, expires_delta=access_token_expires
    )
    token_json = Token(access_token=access_token, token_type='bearer').dict()
    return {
        **response_json,
        **token_json
    }


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

# BUSINESS BACKEND


@app.get('/courses/ping')
async def ping():
    response = requests.get(BUSINESS_BACKEND_URL + '/ping')
    return response.json()


@app.post('/courses/create_course')
async def create_course(request: Request, current_user: dict = Depends(get_current_user)):
    request_json = await request.json()
    request_json['email'] = current_user.email
    response = requests.post(BUSINESS_BACKEND_URL + '/create_course', json=request_json)
    response_json = response.json()

    if response.status_code != 200:
        return public_status_messages.get("error_unexpected")
    if response_json['status'] == 'error':
        return public_status_messages.get(response_json['message'])

    return response_json


@app.get('/profile_setup')
async def profile_setup():
    countries_response = requests.get(BUSINESS_BACKEND_URL + '/countries')
    genres_response = requests.get(BUSINESS_BACKEND_URL + '/course_genres')

    if countries_response.status_code != 200 or genres_response.status_code != 200:
        return public_status_messages.get('error_unexpected')
    if countries_response['status'] == 'error':
        return public_status_messages.get('unavailable_countries')
    if genres_response['status'] == 'error':
        return public_status_messages.get('unavailable_genres')
    return {
        **public_status_messages.get('data_delivered'),
        'locations': countries_response['locations'],
        'course_genres': genres_response['course_genres']
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
