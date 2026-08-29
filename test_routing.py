from graph import route_action, graph

print("--- Testing Hard Rule ---")
assert route_action({"proposed_action": "increase_credit_limit", "confidence_score": 0.99}) == "execute_high_risk_action"

print("--- Testing Auto-Execute ---")
assert route_action({"proposed_action": "send_email", "confidence_score": 0.90}) == "execute_low_risk_action"

print("--- Testing Escalation ---")
assert route_action({"proposed_action": "send_email", "confidence_score": 0.82}) == "execute_high_risk_action"

print("All route_action tests passed!")
