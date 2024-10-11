from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
  _id: Optional[str]
  username: str
  following: int
  followers: int
  num_posts: int