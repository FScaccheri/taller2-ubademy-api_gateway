import uvicorn
import requests

from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from models.login_data import Login

from configuration.status_messages import public_status_messages
from models.token_data import TokenData
from models.token import Token


SECRET_KEY = '944211eb42c3b243739503a1d36225a91317cffe7d1b445add87920b380ddae5'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

USERS_BACKEND_URL = os.environ.get('USERS_BACKEND_URL', 'http://0.0.0.0:8001')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )


def authenticate_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception()
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    response = requests.get(USERS_BACKEND_URL + '/users/' + username)
    if response.status_code == 200:
        return response.json()


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user


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
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception()
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user['disabled']:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


# ENDPOINTS:

@app.get('/')
async def home():
    return public_status_messages.get('hello_api_gateway')


@app.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=public_status_messages.get_message('failed_authentication'),
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['username']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')


@app.get('/users/me')
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user


@app.get('/users/me/items/')
async def read_own_items(current_user: dict = Depends(get_current_active_user)):
    return [{'item_id': 'Foo', 'owner': current_user['username']}]


@app.get('/users/ping', dependencies=[Depends(authenticate_token)])
async def ping():
    response = requests.get(USERS_BACKEND_URL + '/pong')
    return response.json()


@app.post('/login/')
#Request: https://www.starlette.io/requests/
async def login(request: Request):
    #The documentation uses data instead of json but it is not updated
    response = requests.post(USERS_BACKEND_URL + request.url.path, json=await request.json())
    return response.json()


@app.post('/sign_up/')
async def sign_up(request: Request):
    response = requests.post(USERS_BACKEND_URL + '/create/', json=await request.json())
    response_json = response.json()
    if response.status_code != 200 or response_json['status'] == 'error':
        return {'status': 'error', 'message': response_json.get('message')}
    # Creo el token
    user = response_json['user']
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['email']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
