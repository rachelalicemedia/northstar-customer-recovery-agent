def validate_customer_message(message: str) -> tuple[bool, str]:
    """
    Validate a customer message before it is sent.
    """

    prohibited_phrases = [
        "guaranteed delivery",
        "guaranteed overnight",
        "guaranteed next-day",
        "we have shipped",
        "your replacement has shipped",
        "overnight shipping confirmed",
        "next-day shipping confirmed",
    ]

    message_lower = message.lower()

    for phrase in prohibited_phrases:
        if phrase in message_lower:
            return False, (
                f"Message blocked because it contains "
                f"unauthorized promise: '{phrase}'"
            )

    return True, "Message approved"