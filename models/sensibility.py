from typing import Optional
from pydantic import BaseModel

class Sensibility(BaseModel):
  _id: Optional[str]
  id_twitt: str
  confidence: float
  sentiment: str