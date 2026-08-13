import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from models import CustomerAnalysis
from tools import TOOL_FUNCTIONS

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
    }
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