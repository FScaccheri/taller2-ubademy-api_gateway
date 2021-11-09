from pydantic import BaseModel


class CurrentUser(BaseModel):
    email: str
    is_admin: bool = False
