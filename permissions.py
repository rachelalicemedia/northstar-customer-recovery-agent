from dataclasses import dataclass


@dataclass
class PermissionResult:
    allowed: bool
    reason: str


def check_action_permission(
    action: str,
    message: str = "",
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

    if action not in ACTION_TOOLS:
        return PermissionResult(
            allowed=False,
            reason=f"Action '{action}' is not authorized."
        )

    if action == "send_customer_message":

        prohibited_phrases = [
            "guaranteed delivery",
            "guaranteed overnight",
            "guaranteed next-day",
            "will arrive tomorrow",
            "will arrive by tomorrow",
            "replacement has shipped",
            "overnight shipping confirmed",
            "next-day shipping confirmed",
        ]

        message_lower = message.lower()

        for phrase in prohibited_phrases:

            if phrase in message_lower:
                return PermissionResult(
                    allowed=False,
                    reason=(
                        f"Message contains an unauthorized promise: "
                        f"'{phrase}'"
                    )
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