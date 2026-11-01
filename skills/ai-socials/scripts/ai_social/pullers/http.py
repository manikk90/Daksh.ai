"""Minimal JSON-over-HTTPS client (stdlib only) plus URL matching helpers."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

HttpGet = Callable[[str, dict[str, str]], dict[str, Any]]


class ApiError(RuntimeError):
    """A platform API returned an error or an unreadable response."""


def http_get(url: str, headers: dict[str, str]) -> dict[str, Any]:
    """GET ``url`` and decode JSON.

    Raises:
        ApiError: On HTTP errors (body included, token never echoed) or bad JSON.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "ai-social/1.0", **headers})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise ApiError(f"HTTP {exc.code} from {redact(url)}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"network error for {redact(url)}: {exc.reason}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ApiError(f"non-JSON response from {redact(url)}") from exc


def redact(url: str) -> str:
    """Strip access tokens from a URL before it lands in logs or errors."""
    parts = urllib.parse.urlsplit(url)
    query = [(k, "***" if "token" in k.lower() else v) for k, v in urllib.parse.parse_qsl(parts.query)]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query, safe="*")))


def norm_url(url: str) -> str:
    """Normalise a post URL for matching (no scheme, www, query or trailing slash)."""
    parts = urllib.parse.urlsplit((url or "").strip())
    host = parts.netloc.lower().removeprefix("www.")
    host = "x.com" if host == "twitter.com" else host
    return f"{host}{parts.path.rstrip('/')}".lower()
