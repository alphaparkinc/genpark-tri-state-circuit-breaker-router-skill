"""Tri-State Circuit Breaker Router.
100% Python Standard Library.
"""

class TriStateCircuitBreakerRouter:
    """Tri-state circuit breaker router for resilient LLM model failover."""

    def __init__(self, failure_threshold: int = 3, recovery_cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_cooldown = recovery_cooldown_seconds
        self.states = {}

    def get_provider_state(self, provider: str, current_time: float) -> str:
        if provider not in self.states:
            self.states[provider] = {"state": "CLOSED", "failures": 0, "last_failure_time": 0.0, "successes": 0}
            return "CLOSED"
        info = self.states[provider]
        if info["state"] == "OPEN":
            if current_time - info["last_failure_time"] >= self.recovery_cooldown:
                info["state"] = "HALF_OPEN"
                return "HALF_OPEN"
        return info["state"]

    def record_result(self, provider: str, success: bool, current_time: float):
        info = self.states.setdefault(provider, {"state": "CLOSED", "failures": 0, "last_failure_time": 0.0, "successes": 0})
        if success:
            if info["state"] == "HALF_OPEN":
                info["successes"] += 1
                if info["successes"] >= 2:
                    info["state"] = "CLOSED"
                    info["failures"] = 0
                    info["successes"] = 0
            elif info["state"] == "CLOSED":
                info["failures"] = max(0, info["failures"] - 1)
        else:
            info["failures"] += 1
            info["last_failure_time"] = current_time
            if info["state"] in ("CLOSED", "HALF_OPEN") and info["failures"] >= self.failure_threshold:
                info["state"] = "OPEN"
                info["successes"] = 0

    def route_request(self, primary: str, fallback_chain: list, current_time: float) -> dict:
        providers = [primary] + [p for p in fallback_chain if p != primary]
        for p in providers:
            st = self.get_provider_state(p, current_time)
            if st in ("CLOSED", "HALF_OPEN"):
                return {
                    "selected_provider": p,
                    "state": st,
                    "is_fallback": p != primary,
                    "healthy": True
                }
        return {
            "selected_provider": None,
            "state": "ALL_OPEN",
            "is_fallback": True,
            "healthy": False
        }
