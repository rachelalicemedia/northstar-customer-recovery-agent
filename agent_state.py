import json
from enum import Enum

from pydantic import BaseModel, Field

class AgentStatus(str, Enum):
    STARTED = "started"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    AWAITING_HUMAN = "awaiting_human"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentState(BaseModel):
    customer_id: str | None = None
    order_id: str | None = None
    ticket_id: str | None = None
    shipment_id: str | None = None
    tracking_number: str | None = None

    damage_confirmed: bool = False
    requires_human: bool = False
    human_input: str | None = None

    actions_completed: list[str] = Field(default_factory=list)

    current_status: AgentStatus = AgentStatus.STARTED

    def record_action(self, action: str):
        if action not in self.actions_completed:
            self.actions_completed.append(action)

    def set_status(self, status: str):
        self.current_status = status

    def save(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                self.model_dump(mode="json"),
                file,
                indent=4
            )

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.model_validate(data)