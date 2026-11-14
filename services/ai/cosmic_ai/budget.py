"""File-backed USD ledger: reserve the worst-case cost before a paid call, settle after.

Single-process only: the lock is a threading.Lock. Several API workers sharing one
budget need a database row with a transaction instead.
"""

import json
import os
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path


class BudgetExceeded(Exception):
    pass


@dataclass(frozen=True)
class BudgetState:
    limit_usd: float
    spent_usd: float
    reserved_usd: float

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.limit_usd - self.spent_usd - self.reserved_usd)


class BudgetLedger:
    def __init__(self, path: Path, limit_usd: float):
        self.path = path
        self.limit_usd = limit_usd
        self._lock = threading.Lock()

    def _load(self) -> dict:
        if not self.path.is_file():
            return {"spent_usd": 0.0, "reservations": {}, "calls": 0}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def state(self) -> BudgetState:
        with self._lock:
            data = self._load()
        return BudgetState(self.limit_usd, data["spent_usd"], sum(data["reservations"].values()))

    def reserve(self, max_cost_usd: float) -> str:
        if max_cost_usd <= 0:
            raise ValueError("A reservation must be positive")
        with self._lock:
            data = self._load()
            committed = data["spent_usd"] + sum(data["reservations"].values())
            if committed + max_cost_usd > self.limit_usd:
                raise BudgetExceeded(
                    f"Gemini budget exhausted: {committed:.4f} of {self.limit_usd:.2f} USD used"
                )
            reservation = uuid.uuid4().hex
            data["reservations"][reservation] = max_cost_usd
            self._save(data)
            return reservation

    def settle(self, reservation: str, actual_cost_usd: float) -> None:
        """Charge the real cost; an unknown outcome should be settled at the reserved cost."""
        with self._lock:
            data = self._load()
            data["reservations"].pop(reservation, None)
            data["spent_usd"] += actual_cost_usd
            data["calls"] += 1
            self._save(data)

    def release(self, reservation: str) -> None:
        """Drop a reservation only when the request certainly never reached the provider."""
        with self._lock:
            data = self._load()
            data["reservations"].pop(reservation, None)
            self._save(data)
