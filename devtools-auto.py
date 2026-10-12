"""
devtools-auto.py - scriptable DevTools inspection via Playwright.

Captures what you'd manually check in DevTools:
  - Network tab: every request/response with status, timing, size
  - Console: JS errors, warnings, logs
  - Page errors: uncaught exceptions
  - Screenshot at the end

Usage:
  pip install playwright
  playwright install chromium
  python3 devtools-auto.py https://example.com
  python3 devtools-auto.py https://example.com --headed   # watch it run
  python3 devtools-auto.py https://example.com --wait 5000  # ms to wait after load
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("pip install playwright && playwright install chromium")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--wait", type=int, default=3000, help="ms to wait after load")
    ap.add_argument("--out", default="devtools-report.json")
    args = ap.parse_args()

    network: list[dict] = []
    console: list[dict] = []
    page_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page()

        # --- Network tab ---
        def on_response(resp):
            try:
                network.append({
                    "url": resp.url,
                    "method": resp.request.method,
                    "status": resp.status,
                    "content_type": resp.headers.get("content-type", ""),
                    "size": len(resp.headers.get("content-length", "") or ""),
                    "timing_ms": round(resp.request.timing.get("responseEnd", 0)),
                })
            except Exception:
                pass

        page.on("response", on_response)

        # --- Console tab ---
        page.on("console", lambda msg: console.append({
            "type": msg.type,  # log, warning, error, etc.
            "text": msg.text[:500],
        }))

        # --- Uncaught page errors ---
        page.on("pageerror", lambda err: page_errors.append(str(err)[:500]))

        page.goto(args.url, wait_until="networkidle")
        page.wait_for_timeout(args.wait)

        title = page.title()
        page.screenshot(path="devtools-screenshot.png", full_page=False)
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
        },
        "failed_requests": failed[:20],
        "console_errors": errors[:20],
        "page_errors": page_errors[:10],
        "slowest_requests": sorted(network, key=lambda r: r["timing_ms"], reverse=True)[:10],
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Requests: {len(network)} ({len(failed)} failed)")
    print(f"Console errors: {len(errors)}, page errors: {len(page_errors)}")
    print(f"Report: {args.out}, screenshot: devtools-screenshot.png")
    return 0 if not failed and not errors and not page_errors else 1


if __name__ == "__main__":
    sys.exit(main())
