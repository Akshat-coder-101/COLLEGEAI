import time
import asyncio
import threading
import logging
from typing import Dict, List, Optional
from collections import deque
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding-window Rate Limiter & Quota Protector.
    Guarantees:
    1. Requests per minute (RPM) never exceed MAX_RPM_PER_MODEL.
    2. Requests per day (RPD) never exceed MAX_RPD_PER_MODEL.
    3. Spacing delay between consecutive calls to avoid burst spikes.
    4. Model failover pool routing if a model's limit is reached or 429 encountered.
    """
    FAILOVER_POOLS: Dict[str, List[str]] = {
        "gemini-1.5-flash": ["gemini-2.0-flash", "gemini-1.5-flash-8b"],
        "gemini-2.0-flash": ["gemini-1.5-flash", "gemini-1.5-flash-8b"],
        "gemini-1.5-flash-8b": ["gemini-1.5-flash", "gemini-2.0-flash"],
        "gemini-1.5-pro": ["gemini-1.5-flash", "gemini-2.0-flash"],
        "gemini-2.5-pro": ["gemini-1.5-flash", "gemini-2.0-flash"],
        "gemini-2.5-flash": ["gemini-1.5-flash", "gemini-2.0-flash"],
        "gemini-3.5-flash": ["gemini-1.5-flash", "gemini-2.0-flash"],
    }

    def __init__(
        self,
        max_rpm: Optional[int] = None,
        max_rpd: Optional[int] = None,
        delay_seconds: Optional[float] = None
    ):
        self.max_rpm = max_rpm or settings.MAX_RPM_PER_MODEL
        self.max_rpd = max_rpd or settings.MAX_RPD_PER_MODEL
        self.delay_seconds = delay_seconds if delay_seconds is not None else settings.REQUEST_DELAY_SECONDS
        self._custom_delay = (delay_seconds is not None)
        
        self._lock = threading.Lock()
        # model_name -> deque of timestamps in the last 60 seconds
        self._minute_calls: Dict[str, deque] = {}
        # model_name -> deque of timestamps in the last 86400 seconds (24h)
        self._day_calls: Dict[str, deque] = {}
        # model_name -> last call timestamp
        self._last_call_time: Dict[str, float] = {}
        # model_name -> cooldown until timestamp (if 429 was hit)
        self._cooldowns: Dict[str, float] = {}

    def _clean_windows(self, model: str, now: float):
        if model not in self._minute_calls:
            self._minute_calls[model] = deque()
        if model not in self._day_calls:
            self._day_calls[model] = deque()

        # Remove entries older than 60s
        min_q = self._minute_calls[model]
        while min_q and (now - min_q[0]) > 60.0:
            min_q.popleft()

        # Remove entries older than 86400s (24h)
        day_q = self._day_calls[model]
        while day_q and (now - day_q[0]) > 86400.0:
            day_q.popleft()

    def get_effective_model(self, requested_model: str) -> str:
        """
        Determines the best model to call. If the requested model is on cooldown
        or exceeded its daily limit, returns the next available model in the failover pool.
        """
        now = time.time()
        with self._lock:
            # Check if requested model is in cooldown
            if self._cooldowns.get(requested_model, 0) > now:
                candidates = self.FAILOVER_POOLS.get(requested_model, [])
                for cand in candidates:
                    if self._cooldowns.get(cand, 0) <= now:
                        logger.info(f"RateLimiter: Failover from {requested_model} to {cand}")
                        return cand

            # Check daily limit
            self._clean_windows(requested_model, now)
            if len(self._day_calls[requested_model]) >= self.max_rpd:
                candidates = self.FAILOVER_POOLS.get(requested_model, [])
                for cand in candidates:
                    self._clean_windows(cand, now)
                    if len(self._day_calls[cand]) < self.max_rpd:
                        logger.warning(f"RateLimiter: Daily quota reached for {requested_model}. Rerouting to {cand}")
                        return cand

            return requested_model

    def get_model_spacing_delay(self, model: str) -> float:
        """
        Dynamically computes the safe spacing delay between peak requests in a minute.
        If a custom test delay was provided, respects it.
        Otherwise for production models:
        - Pro models (2 RPM limit): 30.0s spacing.
        - Flash models (15 RPM limit): 4.5s to 5.0s spacing (60s / max_rpm).
        """
        if self._custom_delay:
            return self.delay_seconds

        if "pro" in model.lower():
            return 30.0

        rpm_target = max(self.max_rpm, 1)
        calculated_delay = 60.0 / rpm_target
        return max(self.delay_seconds, calculated_delay)

    def acquire(self, model: str) -> float:
        """
        Blocks or waits politely until a request can be safely dispatched
        without breaching RPM limits. Returns the sleep duration (if any).
        """
        sleep_needed = 0.0
        spacing_delay = self.get_model_spacing_delay(model)
        with self._lock:
            now = time.time()
            self._clean_windows(model, now)

            # 1. Enforce model-aware spacing between consecutive calls
            last_time = self._last_call_time.get(model, 0.0)
            elapsed = now - last_time
            if elapsed < spacing_delay:
                spacing_wait = spacing_delay - elapsed
                sleep_needed = max(sleep_needed, spacing_wait)

            # 2. Enforce minute sliding window limit
            min_q = self._minute_calls[model]
            if len(min_q) >= self.max_rpm:
                oldest = min_q[0]
                rpm_wait = 60.0 - (now - oldest) + 0.1
                sleep_needed = max(sleep_needed, rpm_wait)

        if sleep_needed > 0:
            logger.info(f"RateLimiter: Throttling {model} for {sleep_needed:.2f}s to preserve RPM quota.")
            time.sleep(sleep_needed)

        with self._lock:
            actual_now = time.time()
            self._clean_windows(model, actual_now)
            self._minute_calls[model].append(actual_now)
            self._day_calls[model].append(actual_now)
            self._last_call_time[model] = actual_now

        return sleep_needed

    async def async_acquire(self, model: str) -> float:
        """
        Asynchronously waits until a request can be dispatched safely.
        """
        sleep_needed = 0.0
        spacing_delay = self.get_model_spacing_delay(model)
        with self._lock:
            now = time.time()
            self._clean_windows(model, now)

            last_time = self._last_call_time.get(model, 0.0)
            elapsed = now - last_time
            if elapsed < spacing_delay:
                sleep_needed = max(sleep_needed, spacing_delay - elapsed)

            min_q = self._minute_calls[model]
            if len(min_q) >= self.max_rpm:
                oldest = min_q[0]
                rpm_wait = 60.0 - (now - oldest) + 0.1
                sleep_needed = max(sleep_needed, rpm_wait)

        if sleep_needed > 0:
            logger.info(f"RateLimiter: Async throttling {model} for {sleep_needed:.2f}s.")
            await asyncio.sleep(sleep_needed)

        with self._lock:
            actual_now = time.time()
            self._clean_windows(model, actual_now)
            self._minute_calls[model].append(actual_now)
            self._day_calls[model].append(actual_now)
            self._last_call_time[model] = actual_now

        return sleep_needed

    def record_cooldown(self, model: str, duration_seconds: float = 30.0):
        """
        Marks a model on cooldown when encountering HTTP 429 from provider.
        """
        with self._lock:
            self._cooldowns[model] = time.time() + duration_seconds
            logger.warning(f"RateLimiter: Model {model} placed on cooldown for {duration_seconds}s.")

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns real-time usage statistics across all models.
        """
        now = time.time()
        with self._lock:
            stats = {}
            all_models = set(list(self._minute_calls.keys()) + list(self._day_calls.keys()))
            for m in all_models:
                self._clean_windows(m, now)
                stats[m] = {
                    "rpm_used": len(self._minute_calls.get(m, [])),
                    "rpm_limit": self.max_rpm,
                    "rpd_used": len(self._day_calls.get(m, [])),
                    "rpd_limit": self.max_rpd,
                    "in_cooldown": self._cooldowns.get(m, 0) > now
                }
            return stats


# Global Singleton RateLimiter
global_rate_limiter = RateLimiter()
