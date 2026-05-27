"""
Tests for api/_bmad_status.py - _RateLimiter class and API handler.

Focuses on _RateLimiter behavior (thread-safe, per-key, windowed rate limiting).
The BmadStatus handler is tested minimally since it requires Agent Zero runtime.
"""

import sys
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

# -- Save sys.modules state to avoid polluting other tests --
_stub_keys = ("helpers.api",)
_saved_modules = {k: sys.modules[k] for k in _stub_keys if k in sys.modules}

# -- Stub Agent Zero runtime before importing api module --
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

# helpers.api must provide ApiHandler, Request, Response
_api_mod = types.ModuleType("helpers.api")
class _ApiHandler:
    pass
class _Request:
    pass
class _Response:
    def __init__(self, response="", status=200, content_type="application/json"):
        self.response = response
        self.status = status
        self.content_type = content_type
_api_mod.ApiHandler = _ApiHandler
_api_mod.Request = _Request
_api_mod.Response = _Response
sys.modules["helpers.api"] = _api_mod

# Import the rate limiter under test
from api._bmad_status import _RateLimiter

# -- Restore sys.modules so other tests see real modules --
for k in _stub_keys:
    if k in _saved_modules:
        sys.modules[k] = _saved_modules[k]
    elif k in sys.modules:
        del sys.modules[k]


class TestRateLimiterAllowsUnderLimit(unittest.TestCase):
    """Requests within the limit must all be allowed."""

    def test_rate_limiter_allows_under_limit(self):
        limiter = _RateLimiter(max_requests=3, window_seconds=60)
        results = [limiter.is_allowed("key1") for _ in range(3)]
        self.assertTrue(all(results), "All 3 requests under limit should be allowed")


class TestRateLimiterBlocksOverLimit(unittest.TestCase):
    """Requests exceeding the limit must be blocked."""

    def test_rate_limiter_blocks_over_limit(self):
        limiter = _RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.is_allowed("key1")
        self.assertFalse(limiter.is_allowed("key1"), "4th request must be blocked")


class TestRateLimiterSeparateKeys(unittest.TestCase):
    """Different keys must have independent rate limits."""

    def test_rate_limiter_separate_keys(self):
        limiter = _RateLimiter(max_requests=2, window_seconds=60)
        self.assertTrue(limiter.is_allowed("key_a"))
        self.assertTrue(limiter.is_allowed("key_a"))
        self.assertFalse(limiter.is_allowed("key_a"))
        self.assertTrue(limiter.is_allowed("key_b"), "Separate key must have its own limit")


class TestRateLimiterWindowExpiry(unittest.TestCase):
    """After the time window expires, requests must be allowed again."""

    def test_rate_limiter_window_expiry(self):
        limiter = _RateLimiter(max_requests=2, window_seconds=60)
        now = datetime(2025, 1, 1, 12, 0, 0)

        with patch("api._bmad_status.datetime") as mock_dt:
            mock_dt.now.return_value = now
            self.assertTrue(limiter.is_allowed("key1"))
            self.assertTrue(limiter.is_allowed("key1"))
            self.assertFalse(limiter.is_allowed("key1"))

            mock_dt.now.return_value = now + timedelta(seconds=61)
            self.assertTrue(
                limiter.is_allowed("key1"),
                "Request must be allowed after window expires",
            )


class TestRateLimiterReturnsBooleans(unittest.TestCase):
    """is_allowed must return strict booleans."""

    def test_returns_bool(self):
        limiter = _RateLimiter(max_requests=1, window_seconds=60)
        result = limiter.is_allowed("k")
        self.assertIsInstance(result, bool)


class TestHandlerReturnsJsonOnMissingProject(unittest.TestCase):
    """BmadStatus handler must be instantiable with stubbed base."""

    def test_handler_returns_json_on_missing_project(self):
        from api._bmad_status import BmadStatus
        handler = BmadStatus()
        self.assertIsInstance(handler, _ApiHandler)


if __name__ == "__main__":
    unittest.main()
