from pydantic import BaseModel


class CustomerAnalysis(BaseModel):
    sentiment: str
    issue: str
    severity: str
    customer_intent: str
    recommended_action: str
    requires_human: bool
    reason: str