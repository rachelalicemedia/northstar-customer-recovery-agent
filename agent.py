import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from models import CustomerAnalysis
from tools import TOOL_FUNCTIONS
from permissions import (
    check_action_permission,
    is_action_tool,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


TOOLS = [
    {
        "type": "function",
        "name": "get_policy",
        "description": (
            "Retrieve Northstar Supply Co. customer service policies. "
            "Use this whenever you need to determine what actions "
            "are allowed or when a customer issue requires escalation."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_order",
        "description": (
            "Retrieve a Northstar customer order using its order ID. "
            "Use this when the customer provides an order number and "
            "you need to verify order details."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The Northstar order ID, such as NS-1001."
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "send_customer_message",
        "description": (
            "Send a customer service message to a Northstar customer. "
            "Only use this when sending a message is appropriate under "
            "Northstar policy."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_email": {
                    "type": "string",
                    "description": "The customer's email address."
                },
                "message": {
                    "type": "string",
                    "description": "The message to send to the customer."
                }
            },
            "required": [
                "customer_email",
                "message"
            ],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "create_support_ticket",
        "description": (
            "Create a support ticket for human intervention when a "
            "customer issue cannot be safely resolved by the AI."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The Northstar customer ID."
                },
                "order_id": {
                    "type": "string",
                    "description": "The Northstar order ID."
                },
                "issue": {
                    "type": "string",
                    "description": "A concise description of the issue."
                },
                "severity": {
                    "type": "string",
                    "description": "The severity of the issue."
                },
                "summary": {
                    "type": "string",
                    "description": "A concise summary for the human support agent."
                },
                "recommended_action": {
                    "type": "string",
                    "description": "What the human support agent should do next."
                }
            },
            "required": [
                "customer_id",
                "order_id",
                "issue",
                "severity",
                "summary",
                "recommended_action"
            ],
            "additionalProperties": False
        }
    },
]


SYSTEM_PROMPT = """
You are the Northstar Supply Co. Customer Recovery Agent.

Your job is to analyze customer messages and determine the safest
appropriate response according to Northstar's policies.

You MUST retrieve the company policy before recommending an action.

Never invent or assume company policies.

You must not promise or perform actions that Northstar policy does
not authorize.

If policy requires human intervention, set requires_human to true.

Determine:
- sentiment
- issue
- severity
- customer intent
- recommended action
- whether human intervention is required
- reason for your recommendation

You may send customer messages when appropriate.

When a customer has experienced a problem, the message should:
- acknowledge the customer's experience
- apologize sincerely
- avoid making promises that policy does not authorize
- clearly explain the next appropriate step

Do not promise expedited shipping, refunds, discounts, or other
compensation unless company policy explicitly allows it.

If human intervention is required, do not pretend that the issue
has been resolved.

When human intervention is required, create a support ticket
containing the relevant customer, order, issue, severity, summary,
and recommended next action.

Do not merely recommend escalation. Use the support ticket tool
to create the ticket.
"""


def analyze_customer_message(message: str) -> CustomerAnalysis:

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": message
        }
    ]

    while True:

        response = client.responses.create(
            model="gpt-5-mini",
            input=conversation,
            tools=TOOLS
        )

        conversation += response.output

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            break

        for tool_call in tool_calls:

            tool_name = tool_call.name

            if tool_name not in TOOL_FUNCTIONS:
                raise ValueError(
                    f"Unknown tool requested: {tool_name}"
                )

            tool_function = TOOL_FUNCTIONS[tool_name]

            arguments = json.loads(tool_call.arguments)

            if is_action_tool(tool_name):

                permission = check_action_permission(
                    action=tool_name
                )

                if not permission.allowed:

                    result = {
                        "status": "blocked",
                        "reason": permission.reason
                    }

                else:

                    result = tool_function(**arguments)

            else:

                result = tool_function(**arguments)

            conversation.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })

    final_response = client.responses.parse(
        model="gpt-5-mini",
        input=conversation,
        text_format=CustomerAnalysis
    )

    return final_response.output_parsed