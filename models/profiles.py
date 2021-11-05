from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    name: str
    email: str
    country: str
    subscription_type: int
