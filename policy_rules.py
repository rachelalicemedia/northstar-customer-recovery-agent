POLICY_RULES = {
    "send_customer_message": {
        "allowed": True,
        "restrictions": [
            "Cannot promise expedited shipping",
            "Cannot promise a specific delivery date",
            "Cannot independently issue discounts",
            "Cannot independently issue partial refunds",
            "Cannot independently issue store credit",
            "Cannot provide unauthorized compensation",
        ],
    },

    "create_support_ticket": {
        "allowed": True,
        "restrictions": [],
    },

    "ship_replacement": {
        "allowed": True,
        "restrictions": [
            "Requires human approval of replacement and shipping method",
            "Cannot be used to promise delivery before shipment is confirmed",
        ],
    },

    "get_order": {
        "allowed": True,
        "restrictions": [],
    },

    "get_policy": {
        "allowed": True,
        "restrictions": [],
    },
}