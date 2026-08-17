import json
from pathlib import Path
from guardrails import validate_customer_message

POLICY_FILE = Path(__file__).parent / "data" / "policies.md"
ORDERS_FILE = Path(__file__).parent / "data" / "orders.json"


def get_policy() -> str:
    """Retrieve Northstar Supply Co. customer service policies."""

    return POLICY_FILE.read_text(encoding="utf-8")


def get_order(order_id: str) -> dict:
    """Retrieve an order by order ID."""

    orders = json.loads(
        ORDERS_FILE.read_text(encoding="utf-8")
    )

    for order in orders:
        if order["order_id"].lower() == order_id.lower():
            return order

    return {
        "error": f"Order {order_id} was not found."
    }

def send_customer_message(
    customer_email: str,
    message: str
) -> dict:
    """Send a customer service message after guardrail validation."""

    approved, reason = validate_customer_message(message)

    if not approved:
        print("\n--- MESSAGE BLOCKED ---")
        print(reason)
        print("-----------------------\n")

        return {
            "status": "blocked",
            "reason": reason
        }

    print("\n--- CUSTOMER MESSAGE SENT ---")
    print(f"To: {customer_email}")
    print(f"Message: {message}")
    print("-----------------------------\n")

    return {
        "status": "sent",
        "recipient": customer_email,
        "message": message
    }

def create_support_ticket(
    customer_id: str,
    order_id: str,
    issue: str,
    severity: str,
    customer_intent: str,
    summary: str,
    policy_reason: str,
    recommended_action: str
) -> dict:
    """Create a detailed support ticket for human intervention."""

    tickets_file = Path(__file__).parent / "data" / "tickets.json"

    tickets = json.loads(
        tickets_file.read_text(encoding="utf-8")
    )

    ticket_id = f"T-{1000 + len(tickets) + 1}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "issue": issue,
        "severity": severity,
        "customer_intent": customer_intent,
        "summary": summary,
        "policy_reason": policy_reason,
        "recommended_action": recommended_action,
        "status": "open"
    }

    tickets.append(ticket)

    tickets_file.write_text(
        json.dumps(tickets, indent=4),
        encoding="utf-8"
    )

    print("\n--- SUPPORT TICKET CREATED ---")
    print(json.dumps(ticket, indent=4))
    print("-------------------------------\n")

    return ticket

def create_escalation(
    reason: str,
    tool_name: str
) -> dict:
    """Create an escalation when an action cannot be verified."""

    escalation = {
        "status": "escalated",
        "tool": tool_name,
        "reason": reason,
        "message": (
            "Human intervention required because the "
            "requested action could not be verified."
        )
    }

    print("\n--- ACTION ESCALATED ---")
    print(json.dumps(escalation, indent=4))
    print("------------------------\n")

    return escalation

TOOL_FUNCTIONS = {
    "get_policy": get_policy,
    "get_order": get_order,
    "send_customer_message": send_customer_message,
    "create_support_ticket": create_support_ticket,
    "create_escalation": create_escalation,
}