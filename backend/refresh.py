from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable


WEEKLY_REFRESH_INTERVAL = timedelta(days=7)


@dataclass
class RefreshState:
    last_success_at: datetime | None = None
    last_error: str | None = None


class WeeklyRefreshCoordinator:
    """Scheduler-independent coordinator for a once-per-week refresh job."""

    def __init__(
        self,
        refresh_callback: Callable[[], None],
        state: RefreshState | None = None,
    ) -> None:
        self._refresh_callback = refresh_callback
        self.state = state or RefreshState()

    def is_due(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        if self.state.last_success_at is None:
            return True
        return current - self.state.last_success_at >= WEEKLY_REFRESH_INTERVAL

    def run_if_due(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        if not self.is_due(current):
            return False
        try:
            self._refresh_callback()
        except Exception as exc:
            self.state.last_error = str(exc)
            raise
        self.state.last_success_at = current
        self.state.last_error = None
        return True
