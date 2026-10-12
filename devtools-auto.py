"""
devtools-auto.py - scriptable DevTools inspection via Playwright.

Captures what you'd manually check in DevTools:
  - Network tab: every request/response with status, wall-clock timing, size
  - Console: JS errors, warnings, logs
  - Page errors: uncaught exceptions
  - Security headers on the main document
  - Full-page screenshot at the end

Usage:
  uv sync
  uv run playwright install chromium
  uv run devtools-auto.py https://example.com
  uv run devtools-auto.py https://example.com --headed   # watch it run
  uv run devtools-auto.py https://example.com --wait 5000  # ms to wait after load
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("uv sync  (or: pip install playwright && playwright install chromium)")

# Truncation cap for console/page-error text. Flagged in output when hit.
TEXT_CAP = 2000

# Security headers extracted from the main document response.
SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
]


def parse_content_length(headers: dict) -> int:
    """Return Content-Length as int, or 0 if absent/malformed.

    Note: chunked responses have no Content-Length; 0 means "unknown",
    not "empty". See SCOPE.md.
    """
    try:
        return int(headers.get("content-length", 0) or 0)
    except (ValueError, TypeError):
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--wait", type=int, default=3000, help="ms to wait after load")
    ap.add_argument("--out", default="devtools-report.json")
    args = ap.parse_args()

    network: list[dict] = []
    console: list[dict] = []
    page_errors: list[dict] = []
    security_headers: dict = {}
    handler_errors = 0
    request_start: dict = {}  # id(request) -> monotonic start time

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page()

        # --- Network tab: wall-clock timing per request ---
        def on_request(req):
            request_start[id(req)] = time.monotonic()

        def on_response(resp):
            nonlocal handler_errors
            try:
                req = resp.request
                start = request_start.pop(id(req), None)
                elapsed_ms = round((time.monotonic() - start) * 1000) if start else -1
                entry = {
                    "url": resp.url,
                    "method": req.method,
                    "status": resp.status,
                    "content_type": resp.headers.get("content-type", ""),
                    # From Content-Length header; 0 = unknown (e.g. chunked).
                    "size_bytes": parse_content_length(resp.headers),
                    # Wall-clock ms from request to response. -1 = unknown.
                    "timing_ms": elapsed_ms,
                }
                network.append(entry)
                # Capture security headers from the top-level document.
                if req.resource_type == "document" and resp.url.rstrip("/") == args.url.rstrip("/"):
                    for h in SECURITY_HEADERS:
                        if h in resp.headers:
                            security_headers[h] = resp.headers[h]
            except Exception as e:
                # Never silently drop: count it so the report shows the gap.
                handler_errors += 1

        page.on("request", on_request)
        page.on("response", on_response)

        # --- Console tab ---
        def on_console(msg):
            text = msg.text
            console.append({
                "type": msg.type,  # log, warning, error, etc.
                "text": text[:TEXT_CAP],
                "truncated": len(text) > TEXT_CAP,
            })

        page.on("console", on_console)

        # --- Uncaught page errors ---
        def on_page_error(err):
            text = str(err)
            page_errors.append({
                "text": text[:TEXT_CAP],
                "truncated": len(text) > TEXT_CAP,
            })

        page.on("pageerror", on_page_error)

        # domcontentloaded + fixed wait: networkidle hangs on SPAs with
        # polling, WebSockets, or long-lived connections.
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(args.wait)

        title = page.title()
        page.screenshot(path="devtools-screenshot.png", full_page=True)
        browser.close()

    failed = [r for r in network if r["status"] >= 400]
    errors = [c for c in console if c["type"] == "error"]

    report = {
        "url": args.url,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "summary": {
            "total_requests": len(network),
            "failed_requests": len(failed),
            "console_errors": len(errors),
            "console_warnings": len([c for c in console if c["type"] == "warning"]),
            "page_errors": len(page_errors),
            "handler_errors": handler_errors,
        },
        "security_headers": security_headers,
        "failed_requests": failed[:20],
        "console_errors": errors[:20],
        "page_errors": page_errors[:10],
        "slowest_requests": sorted(
            [r for r in network if r["timing_ms"] >= 0],
            key=lambda r: r["timing_ms"], reverse=True,
        )[:10],
        "notes": [
            "size_bytes comes from the Content-Length header; 0 means unknown (e.g. chunked encoding), not empty.",
            "timing_ms is wall-clock per request; -1 means the start was not observed.",
            "A clean report means this one headless Chromium load produced no failures. See SCOPE.md.",
        ],
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Requests: {len(network)} ({len(failed)} failed)")
    print(f"Console errors: {len(errors)}, page errors: {len(page_errors)}")
    if handler_errors:
        print(f"WARNING: {handler_errors} response(s) failed to record (see handler_errors)")
    print(f"Report: {args.out}, screenshot: devtools-screenshot.png")
    return 0 if not failed and not errors and not page_errors else 1


if __name__ == "__main__":
    sys.exit(main())
