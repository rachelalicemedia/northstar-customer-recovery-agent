import os

from dotenv import load_dotenv
from openai import OpenAI

from models import CustomerAnalysis
from tools import get_policy

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_customer_message(message: str) -> CustomerAnalysis:

    tools = [
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
        }
    ]

    input_messages = [
        {
            "role": "system",
            "content": """
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
        },
        {
            "role": "user",
            "content": message
        }
    ]

    response = client.responses.create(
        model="gpt-5-mini",
        input=input_messages,
        tools=tools
    )

    # Preserve the complete model response
    input_messages += response.output

    # Execute any requested tools
    for item in response.output:

        if item.type == "function_call":

            if item.name == "get_policy":

                policy = get_policy()

                input_messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": policy
                })

    # Ask the model for the final structured decision
    final_response = client.responses.parse(
        model="gpt-5-mini",
        input=input_messages,
        text_format=CustomerAnalysis
    )

    return final_response.output_parsed