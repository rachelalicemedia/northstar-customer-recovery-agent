from agent import analyze_customer_message
from permissions import check_action_permission
from verification import verify_tool_result


def test_time_sensitive_damage_requires_human():
    message = """
    My 100ft Heavy-Duty Garden Hose arrived cracked.
    I need a replacement delivered by tomorrow because
    I have a project scheduled.
    My order number is NS-1001.
    """

    result = analyze_customer_message(
        message,
        state_file="agent_state_test.json"
    )

    assert result.requires_human is True

def test_damaged_product_without_deadline_avoids_unauthorized_promise():
    message = """
    My 100ft Heavy-Duty Garden Hose arrived cracked.
    I would like a replacement.
    My order number is NS-1001.
    """

    result = analyze_customer_message(
        message,
        state_file="agent_state_test.json"
    )

    assert "expedited" not in result.recommended_action.lower()
    assert "guaranteed" not in result.recommended_action.lower()
    assert "tomorrow" not in result.recommended_action.lower()

def test_policy_blocks_guaranteed_delivery_promise():
    permission = check_action_permission(
        action="send_customer_message",
        message=(
            "Your replacement will arrive tomorrow "
            "with guaranteed next-day delivery."
        )
    )

    assert permission.allowed is False

def test_failed_shipment_is_not_verified():
    result = {
        "status": "failed",
        "order_id": "NS-1001",
        "product_id": "P-001",
        "shipping_method": "simulate_failure",
        "reason": "Simulated fulfillment system failure."
    }

    verified, reason = verify_tool_result(
        "ship_replacement",
        result
    )

    assert verified is False
    assert "valid shipment" in reason