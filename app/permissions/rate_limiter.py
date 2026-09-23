import time
from collections import defaultdict

class RateLimiter:
    def __init__(self) -> None:
        self._calls: dict[tuple[str, str], list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str, tool_name: str, limit_per_minute: int) -> bool:
        key = (user_id, tool_name)
        window_start = time.time() - 60
        self._calls[key] = [t for t in self._calls[key] if t > window_start]
        return len(self._calls[key]) < limit_per_minute

    def record_call(self, user_id: str, tool_name: str) -> None:
        key = (user_id, tool_name)
        self._calls[key].append(time.time())