"""
Tests that the rate limiter only trusts forwarded headers from configured
proxies, preventing X-Forwarded-For spoofing bypass.
"""

from unittest.mock import Mock

from src.api.middleware.rate_limit import RateLimitMiddleware


def _make_request(client_host, headers=None):
    request = Mock()
    request.client = Mock()
    request.client.host = client_host
    request.headers = headers or {}
    return request


def _middleware(monkeypatch, trusted=""):
    monkeypatch.setenv("TRUSTED_PROXIES", trusted)
    return RateLimitMiddleware(app=Mock())


def test_forwarded_header_ignored_from_untrusted_peer(monkeypatch):
    mw = _middleware(monkeypatch, trusted="")
    req = _make_request("203.0.113.9", {"X-Forwarded-For": "1.2.3.4"})
    # Direct peer is not trusted -> spoofed header ignored, use real peer IP.
    assert mw._get_client_ip(req) == "203.0.113.9"


def test_forwarded_header_honoured_from_trusted_proxy(monkeypatch):
    mw = _middleware(monkeypatch, trusted="10.0.0.1")
    req = _make_request("10.0.0.1", {"X-Forwarded-For": "1.2.3.4, 10.0.0.1"})
    # Direct peer is a trusted proxy -> use the originating client IP.
    assert mw._get_client_ip(req) == "1.2.3.4"


def test_real_ip_header_only_from_trusted_proxy(monkeypatch):
    mw = _middleware(monkeypatch, trusted="10.0.0.1")
    req = _make_request("10.0.0.1", {"X-Real-IP": "5.6.7.8"})
    assert mw._get_client_ip(req) == "5.6.7.8"
