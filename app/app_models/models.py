from pydantic import BaseModel
from datetime import datetime


class ProfileVisitedInput(BaseModel):
    user_id: str
    visitor_id: str


class ProfileVisitedEntry(BaseModel):
    user_id: str
    visitor_id: str
    visited_at: datetime
