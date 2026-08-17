from policy_rules import POLICY_RULES
from policy_checker import check_message_against_policy
from dataclasses import dataclass


@dataclass
class PermissionResult:
    allowed: bool
    reason: str


def check_action_permission(
    action: str,
    message: str = ""
) -> PermissionResult:

    """
    Determine whether an action is permitted under
    Northstar's business policies.
    """

    if action not in POLICY_RULES:
        return PermissionResult(
            allowed=False,
            reason=f"Action '{action}' is not defined by policy."
        )

    policy = POLICY_RULES[action]

    if not policy["allowed"]:
        return PermissionResult(
            allowed=False,
            reason=f"Policy does not authorize action '{action}'."
        )

    if action == "send_customer_message":

        message_lower = message.lower()

        prohibited_patterns = [
            "will arrive tomorrow",
            "will arrive by tomorrow",
            "guaranteed delivery",
            "guaranteed overnight",
            "guaranteed next-day",
            "overnight shipping confirmed",
            "next-day shipping confirmed",
        ]

        for pattern in prohibited_patterns:

            if pattern in message_lower:
                return PermissionResult(
                    allowed=False,
                    reason=(
                        "Northstar policy prohibits the AI from "
                        f"making this promise: '{pattern}'."
                    )
                )

        semantic_result = check_message_against_policy(message)

        if not semantic_result.allowed:
            return PermissionResult(
                allowed=False,
                reason=semantic_result.reason
            )

    return PermissionResult(
        allowed=True,
        reason="Action is authorized by Northstar policy."
    )

READ_ONLY_TOOLS = {
    "get_policy",
    "get_order",
}


ACTION_TOOLS = {
    "send_customer_message",
    "create_support_ticket",
}


def is_action_tool(tool_name: str) -> bool:
    return tool_name in ACTION_TOOLS