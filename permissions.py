from dataclasses import dataclass


@dataclass
class PermissionResult:
    allowed: bool
    reason: str


def check_action_permission(
    action: str,
    requires_human: bool = False
) -> PermissionResult:
    """
    Determine whether the agent is permitted to execute an action.
    """

    if requires_human:
        return PermissionResult(
            allowed=False,
            reason="This action requires human intervention."
        )

    allowed_actions = {
        "send_customer_message",
        "create_support_ticket",
    }

    if action not in allowed_actions:
        return PermissionResult(
            allowed=False,
            reason=f"Action '{action}' is not authorized."
        )

    return PermissionResult(
        allowed=True,
        reason="Action is authorized."
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