from pydantic import BaseModel

class Login(BaseModel):
    email: str
    hashed_password: str

    def __init__(self, data_dict: dict):
        self.email = data_dict['email']
        self.hashed_password = data_dict['password']