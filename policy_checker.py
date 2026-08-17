import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def check_message_against_policy(message: str) -> PolicyDecision:

    policy = """
Northstar Supply Co. Customer Service Policies:

- The AI may handle issues when company policy clearly authorizes the resolution.
- The AI must not invent policies or make unauthorized promises.
- Damaged products may qualify for replacement or refund.
- Standard replacement shipping may be provided at no additional cost.
- The AI may NOT promise expedited shipping.
- If a customer requires delivery by a specific date, the case must be escalated.
- The AI may not promise a specific delivery date.
- The AI may explain the return policy but may not approve exceptions.
- The AI may not independently issue discounts, partial refunds, store credit,
  free expedited shipping, or other unauthorized compensation.
- Situations outside policy or situations where information is insufficient
  must be escalated to a human.
"""

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a policy authorization checker for Northstar Supply Co. "
                    "Determine whether the proposed customer message complies with "
                    "Northstar policy. Do not rewrite the message. "
                    "If there is uncertainty about whether the message violates "
                    "policy, deny authorization."
                ),
            },
            {
                "role": "user",
                "content": f"""
{policy}

Proposed customer message:

{message}

Determine whether the message is authorized under the policy.
""",
            },
        ],
        text_format=PolicyDecision,
    )

    return response.output_parsed