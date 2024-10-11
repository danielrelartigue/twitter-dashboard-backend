from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Twitt(BaseModel):
  _id: Optional[str]
  user_id: str
  message: str
  num_likes: int
  num_retweets: int
  created_at: datetime
