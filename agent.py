import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from models import CustomerAnalysis
from tools import TOOL_FUNCTIONS
from logger import log_event
from permissions import (
    check_action_permission,
    is_action_tool,
)
from verification import verify_tool_result

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
            "Create a detailed support ticket for human intervention "
            "when a customer issue cannot be safely resolved by the AI."
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
                "customer_intent": {
                    "type": "string",
                    "description": "What the customer is asking Northstar to do."
                },
                "summary": {
                    "type": "string",
                    "description": "A concise summary for the human support agent."
                },
                "policy_reason": {
                    "type": "string",
                    "description": "Why the AI cannot safely resolve the issue."
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
                "customer_intent",
                "summary",
                "policy_reason",
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

When human intervention is required, create a detailed support ticket.

The ticket must include:
- customer ID
- order ID
- issue
- severity
- customer intent
- concise summary
- the policy reason escalation is required
- recommended next action for the human agent

The ticket should allow a human agent to understand the situation
without rereading the original customer conversation.

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
                    action=tool_name,
                    message=arguments.get("message", "")
                )

                log_event(
                    "permission_check",
                    {
                        "tool": tool_name,
                        "allowed": permission.allowed,
                        "reason": permission.reason
                    }
                )

                if not permission.allowed:

                    result = {
                        "status": "blocked",
                        "reason": permission.reason
                    }


                else:

                    log_event(
                        "tool_called",
                        {
                            "tool": tool_name,
                            "arguments": arguments
                        }
                    )

                    result = tool_function(**arguments)

                    verified, verification_reason = verify_tool_result(
                        tool_name,
                        result
                    )

                    log_event(
                        "verification_check",
                        {
                            "tool": tool_name,
                            "verified": verified,
                            "reason": verification_reason
                        }
                    )

                    if not verified:
                        log_event(
                            "verification_failure",
                            {
                                "tool": tool_name,
                                "reason": verification_reason
                            }
                        )

                        escalation = TOOL_FUNCTIONS["create_escalation"](
                            reason=verification_reason,
                            tool_name=tool_name
                        )

                        result = escalation


            else:

                log_event(
                    "tool_called",
                    {
                        "tool": tool_name,
                        "arguments": arguments
                    }
                )

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