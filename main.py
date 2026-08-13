from agent import analyze_customer_message


message = """
My garden hose arrived cracked and I need it for a project tomorrow.
Can you send me another one?
"""

analysis = analyze_customer_message(message)

print(analysis)