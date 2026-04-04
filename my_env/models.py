from pydantic import BaseModel
from typing import List

class Observation(BaseModel):
    ticket_id: str
    customer_message: str
    status: str
    history: List[str]

class Action(BaseModel):
    reply: str
    mark_resolved: bool