import time
import pytest
from app.services.rate_limiter import RateLimiter
from app.services.llm_service import get_llm_service, MockLLMProvider
from app.config import settings


def test_rate_limiter_spacing_and_rpm():
    # Instantiate RateLimiter with tight limits for testing: 3 RPM, 0.05s spacing
    limiter = RateLimiter(max_rpm=3, max_rpd=10, delay_seconds=0.05)
    test_model = "test-flash"

    # Call 1: Immediate
    t0 = time.time()
    limiter.acquire(test_model)
    t1 = time.time()
    assert (t1 - t0) < 0.1

    # Call 2: Spacing delay applied
    limiter.acquire(test_model)
    t2 = time.time()
    assert (t2 - t1) >= 0.04

    # Call 3: Spacing delay applied
    limiter.acquire(test_model)

    stats = limiter.get_stats()
    assert stats[test_model]["rpm_used"] == 3
    assert stats[test_model]["rpd_used"] == 3


def test_rate_limiter_cooldown_and_failover():
    limiter = RateLimiter(max_rpm=5, max_rpd=20, delay_seconds=0.0)
    primary_model = "gemini-2.5-pro"

    # Initially effective model is the primary model
    assert limiter.get_effective_model(primary_model) == primary_model

    # Record 429 cooldown on primary model
    limiter.record_cooldown(primary_model, duration_seconds=5.0)

    # Should automatically fail over to next model in pool (e.g. gemini-1.5-pro or gemini-2.5-flash)
    fallback = limiter.get_effective_model(primary_model)
    assert fallback != primary_model
    assert fallback in RateLimiter.FAILOVER_POOLS[primary_model]


def test_rate_limiter_daily_quota_protection():
    limiter = RateLimiter(max_rpm=10, max_rpd=2, delay_seconds=0.0)
    primary = "gemini-2.5-flash"

    limiter.acquire(primary)
    limiter.acquire(primary)

    # Daily quota (2) reached -> failover to alternative candidate in pool
    effective = limiter.get_effective_model(primary)
    assert effective != primary
    assert effective in RateLimiter.FAILOVER_POOLS[primary]


def test_multi_model_role_resolution():
    planner_llm = get_llm_service(role="planner")
    assert planner_llm.model_name == settings.MODEL_PLANNER

    analyzer_llm = get_llm_service(role="analyzer")
    assert analyzer_llm.model_name == settings.MODEL_ANALYZER

    hypo_llm = get_llm_service(role="hypothesis")
    assert hypo_llm.model_name == settings.MODEL_HYPOTHESIS

    reviewer_llm = get_llm_service(role="reviewer")
    assert reviewer_llm.model_name == settings.MODEL_REVIEWER


@pytest.mark.asyncio
async def test_async_rate_limiter_acquire():
    limiter = RateLimiter(max_rpm=5, max_rpd=10, delay_seconds=0.05)
    model = "async-test-model"

    t0 = time.time()
    await limiter.async_acquire(model)
    await limiter.async_acquire(model)
    t1 = time.time()
    assert (t1 - t0) >= 0.04
