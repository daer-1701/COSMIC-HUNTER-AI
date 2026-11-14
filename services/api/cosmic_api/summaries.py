"""Gemini summary plumbing for the API: configuration gate, ledger, cache, rate limit."""

import hashlib
import threading
import time
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Any

from cosmic_ai.budget import BudgetLedger
from google import genai
from google.genai import types

from cosmic_api.settings import Settings


def missing_configuration(settings: Settings) -> str | None:
    """Why paid calls are off, or None when every control is configured."""
    if not settings.gemini_enabled:
        return "Gemini summaries are disabled (GEMINI_ENABLED=false)"
    if not settings.gemini_api_key:
        return "Gemini is not configured: GEMINI_API_KEY is empty"
    if not settings.gemini_model:
        return "Gemini is not configured: GEMINI_MODEL is empty"
    if settings.gemini_input_usd_per_mtok <= 0 or settings.gemini_output_usd_per_mtok <= 0:
        return "Gemini is not configured: token prices are not set"
    if settings.gemini_budget_usd <= 0:
        return "Gemini is not configured: GEMINI_BUDGET_USD must be positive"
    return None


@lru_cache(maxsize=4)
def _client(api_key: str, timeout_seconds: float) -> genai.Client:
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
    )


def get_gemini_client(settings: Settings) -> Any:
    return _client(settings.gemini_api_key, settings.gemini_timeout_seconds)


@lru_cache(maxsize=4)
def get_ledger(path: Path, limit_usd: float) -> BudgetLedger:
    """One ledger object per file so every request shares the same lock."""
    return BudgetLedger(path, limit_usd)


class RateLimiter:
    def __init__(self):
        self._calls: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self, max_per_minute: int) -> float | None:
        """Record a call and return None, or return seconds to wait."""
        now = time.monotonic()
        with self._lock:
            while self._calls and now - self._calls[0] >= 60:
                self._calls.popleft()
            if len(self._calls) >= max_per_minute:
                return 60 - (now - self._calls[0])
            self._calls.append(now)
            return None


rate_limiter = RateLimiter()
summary_cache: dict[str, Any] = {}


def cache_key(slug: str, model: str, prompt: str) -> str:
    return hashlib.sha256(f"{slug}\n{model}\n{prompt}".encode()).hexdigest()
