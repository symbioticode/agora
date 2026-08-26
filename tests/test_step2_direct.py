from datetime import datetime
from zoneinfo import ZoneInfo

from scripts.step2_direct import estimated_cost, in_window, usage_cost


def test_window_is_half_open():
    tz = ZoneInfo("America/Toronto")
    assert in_window(datetime(2026, 8, 10, 0, 0, tzinfo=tz))
    assert in_window(datetime(2026, 8, 10, 3, 59, tzinfo=tz))
    assert not in_window(datetime(2026, 8, 10, 4, 0, tzinfo=tz))
    assert not in_window(datetime(2026, 8, 9, 23, 59, tzinfo=tz))


def test_cost_estimate():
    assert estimated_cost("anthropic", 1_000_000, 1_000_000) == 18.0
    assert estimated_cost("deepseek", 1_000_000, 1_000_000) == 6.0


def test_anthropic_cache_is_costed():
    cost = usage_cost("anthropic", {
        "input_tokens": 0, "cache_creation_input_tokens": 1_000_000,
        "cache_read_input_tokens": 0, "output_tokens": 0,
    })
    assert cost == 3.75
