from dataclasses import dataclass, field


@dataclass
class Observation:
    ticket_id: str
    customer_message: str
    status: str
    history: list[str] = field(default_factory=list)


@dataclass
class Action:
    reply: str
    mark_resolved: bool
