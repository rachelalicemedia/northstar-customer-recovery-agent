from agent import resume_agent


print("\n--- RESUMING WORKFLOW ---")

result = resume_agent(
    """
    Human support has confirmed that product P-001 is currently in stock.
    Next-day shipping is available and has been approved.
    The replacement can be shipped today.
    """
)

print("\n--- RESUMED FINAL ANALYSIS ---")
print(result)
print("-----------------------------\n")