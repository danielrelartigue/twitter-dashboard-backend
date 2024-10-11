from pydantic import BaseModel
from typing import Optional

class Hashtag(BaseModel):
  _id: Optional[str]
  title: str