from agent import analyze_customer_message


message = """
Customer: Sarah Johnson
Customer ID: C-001
Email: sarah@example.com
Order ID: NS-1001

My 100ft Heavy-Duty Garden Hose arrived cracked. I need a replacement
because I have a project tomorrow, so I need the replacement delivered
by tomorrow.
"""


result = analyze_customer_message(message)


print("\n--- FINAL ANALYSIS ---")
print(result)
print("----------------------\n")