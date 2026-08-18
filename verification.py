def verify_tool_result(tool_name: str, result) -> tuple[bool, str]:
    """
    Verify that a tool actually completed its intended action.
    """

    if not isinstance(result, dict):
        return False, "Tool returned an unexpected result format."

    if tool_name == "send_customer_message":

        if result.get("status") == "sent":
            return True, "Customer message was successfully sent."

        if result.get("status") == "blocked":
            return False, result.get(
                "reason",
                "Customer message was blocked."
            )

        return False, "Customer message tool did not confirm delivery."

    if tool_name == "create_support_ticket":

        if result.get("ticket_id"):
            return True, (
                f"Support ticket {result['ticket_id']} "
                "was successfully created."
            )

        return False, "Support ticket tool did not return a ticket ID."

    if tool_name == "ship_replacement":

        if (
            result.get("status") == "shipped"
            and result.get("shipment_id")
            and result.get("tracking_number")
        ):
            return True, (
                f"Replacement shipment {result['shipment_id']} "
                "was successfully created."
            )

        return False, (
            "Replacement shipment tool did not confirm "
            "a valid shipment."
        )

    if tool_name in {"get_order", "get_policy"}:

        if result:
            return True, "Information was successfully retrieved."

        return False, "Tool returned no information."

    return True, "Tool execution completed."