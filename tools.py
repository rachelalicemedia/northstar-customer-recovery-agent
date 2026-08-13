import json
from pathlib import Path


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


TOOL_FUNCTIONS = {
    "get_policy": get_policy,
    "get_order": get_order,
}