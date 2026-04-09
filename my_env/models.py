from pydantic import BaseModel, Field


class Observation(BaseModel):
    ticket_id: str = Field(..., description="Ticket identifier for the active support case.")
    task_name: str = Field(..., description="Task id for the active scenario.")
    difficulty: str = Field(..., description="Difficulty band for the active scenario.")
    customer_message: str = Field(..., description="Latest customer-facing message.")
    status: str = Field(..., description="Current ticket status, usually open or resolved.")
    customer_profile: dict[str, str] = Field(
        default_factory=dict,
        description="Operational context about the customer such as tier, sentiment, and order value.",
    )
    policy_hint: str = Field(
        ...,
        description="Short policy reminder the agent should respect while resolving the ticket.",
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="Checklist-style success conditions for the current scenario.",
    )
    history: list[str] = Field(default_factory=list, description="Chronological agent reply history.")


class Action(BaseModel):
    reply: str = Field(..., description="Support agent reply for the current turn.")
    mark_resolved: bool = Field(..., description="Whether the agent claims the ticket is resolved.")


class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="Normalized reward for the current step.")
    empathy: float = Field(0.0, ge=0.0, le=0.15)
    intent_coverage: float = Field(0.0, ge=0.0, le=0.25)
    resolution_quality: float = Field(0.0, ge=0.0, le=0.2)
    policy_compliance: float = Field(0.0, ge=0.0, le=0.15)
    deescalation: float = Field(0.0, ge=0.0, le=0.1)
    ownership: float = Field(0.0, ge=0.0, le=0.1)
    clarity: float = Field(0.0, ge=0.0, le=0.05)
    penalties: float = Field(0.0, le=0.0, description="Negative adjustments for weak or repetitive behavior.")
