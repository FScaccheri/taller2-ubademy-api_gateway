from typing import List
from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    name: str
    country: str
    subscription_type: str
    interesting_genres: List[str]
