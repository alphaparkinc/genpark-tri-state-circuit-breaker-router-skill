"""Example usage for Tri-State Circuit Breaker Router."""
from client import TriStateCircuitBreakerRouter
import json
import time

cb = TriStateCircuitBreakerRouter(failure_threshold=2, recovery_cooldown_seconds=15.0)
now = time.time()

# 1. Normal call to primary
route = cb.route_request("claude-3-5-sonnet", ["gpt-4o", "deepseek-v3"], now)
print("Route 1:", json.dumps(route))

# 2. Simulate 2 consecutive failures on primary
cb.record_result("claude-3-5-sonnet", False, now)
cb.record_result("claude-3-5-sonnet", False, now)

# 3. Call routes to fallback
route2 = cb.route_request("claude-3-5-sonnet", ["gpt-4o", "deepseek-v3"], now)
print("Route 2 (Fallback):", json.dumps(route2))
