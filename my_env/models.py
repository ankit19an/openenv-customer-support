from pydantic import BaseModel, Field


class Observation(BaseModel):
    ticket_id: str = Field(..., description="Ticket identifier for the active support case.")
    customer_message: str = Field(..., description="Latest customer-facing message.")
    status: str = Field(..., description="Current ticket status, usually open or resolved.")
    history: list[str] = Field(default_factory=list, description="Chronological agent reply history.")


class Action(BaseModel):
    reply: str = Field(..., description="Support agent reply for the current turn.")
    mark_resolved: bool = Field(..., description="Whether the agent claims the ticket is resolved.")


class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="Normalized reward for the current step.")
    empathy: float = Field(0.0, ge=0.0, le=0.2)
    intent_coverage: float = Field(0.0, ge=0.0, le=0.4)
    resolution_quality: float = Field(0.0, ge=0.0, le=0.3)
    clarity: float = Field(0.0, ge=0.0, le=0.1)
    penalties: float = Field(0.0, le=0.0, description="Negative adjustments for weak or repetitive behavior.")
