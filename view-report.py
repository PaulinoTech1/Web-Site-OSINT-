"""
view-report.py - Generate a self-contained HTML report from devtools-auto.py JSON output.

Usage:
  python3 view-report.py devtools-report.json
  python3 view-report.py devtools-report.json -o report.html

Opens a clean, readable report in any browser. No server needed, no dependencies.
Everything is embedded in the single HTML file.
"""

import argparse
import html
import json
import sys


def esc(s):
    return html.escape(str(s or ""))


def section(title, rows, headers):
    if not rows:
        return f"<h2>{esc(title)}</h2><p class='muted'>None found. Good.</p>"
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = []
    for r in rows:
        tds = "".join(f"<td>{esc(r.get(h, ''))}</td>" for h in headers)
        trs.append(f"<tr>{tds}</tr>")
    return f"<h2>{esc(title)} ({len(rows)})</h2><table><tr>{th}</tr>{''.join(trs)}</table>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="JSON report from devtools-auto.py")
    ap.add_argument("-o", "--output", default="report.html")
    args = ap.parse_args()

    try:
        with open(args.input) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        sys.exit(f"Cannot read {args.input}: {e}")

    summary = data.get("summary", {})
    badge_color = "#2d7d2d" if (
        summary.get("failed_requests", 0) == 0
        and summary.get("console_errors", 0) == 0
        and summary.get("page_errors", 0) == 0
    ) else "#b3402a"
    badge_text = "CLEAN" if badge_color == "#2d7d2d" else "ISSUES FOUND"

    failed = data.get("failed_requests", [])
    for r in failed:
        r["url"] = r.get("url", "")[:100]

    slowest = data.get("slowest_requests", [])
    for r in slowest:
        r["url"] = r.get("url", "")[:100]

    sec_headers = data.get("security_headers", {})
    sec_rows = "".join(
        f"<tr><td><code>{esc(k)}</code></td><td>{esc(v[:200])}</td></tr>"
        for k, v in sec_headers.items()
    )
    sec_section = (
        f"<h2>Security Headers</h2><table>"
        f"<tr><th>Header</th><th>Value</th></tr>{sec_rows}</table>"
        if sec_rows
        else "<h2>Security Headers</h2><p class='muted'>None of the checked headers present on the main document.</p>"
    )

    notes = data.get("notes", [])
    notes_html = "".join(f"<li>{esc(n)}</li>" for n in notes)
    notes_section = f"<h2>Reading this report</h2><ul>{notes_html}</ul>" if notes_html else ""

    handler_warn = ""
    if summary.get("handler_errors", 0):
        handler_warn = (f"<p style='color:#b3402a'><strong>Warning:</strong> "
                        f"{summary['handler_errors']} response(s) failed to record.</p>")

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site Inspection Report</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 1000px;
         margin: 0 auto; padding: 24px; background: #f7f7f7; color: #222; }}
  h1 {{ margin-bottom: 4px; }}
  .meta {{ color: #666; margin-bottom: 16px; }}
  .badge {{ display: inline-block; padding: 6px 16px; border-radius: 4px;
            color: #fff; font-weight: bold; background: {badge_color}; }}
  .cards {{ display: flex; gap: 12px; margin: 16px 0; flex-wrap: wrap; }}
  .card {{ background: #fff; border: 1px solid #ddd; border-radius: 6px;
           padding: 12px 18px; min-width: 120px; }}
  .card .n {{ font-size: 28px; font-weight: bold; }}
  .card .l {{ color: #666; font-size: 13px; }}
  h2 {{ margin-top: 32px; border-bottom: 2px solid #ddd; padding-bottom: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border: 1px solid #ddd; margin-top: 8px; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #eee;
            word-break: break-all; }}
  th {{ background: #f0f0f0; }}
  .muted {{ color: #888; }}
  footer {{ margin-top: 40px; color: #999; font-size: 12px; }}
</style>
</head>
<body>
<h1>Site Inspection Report</h1>
<div class="meta">{esc(data.get('url', ''))}<br>Checked: {esc(data.get('checked_at', ''))}</div>
<span class="badge">{badge_text}</span>
{handler_warn}
<div class="cards">
  <div class="card"><div class="n">{summary.get('total_requests', 0)}</div><div class="l">Total requests</div></div>
  <div class="card"><div class="n">{summary.get('failed_requests', 0)}</div><div class="l">Failed requests</div></div>
  <div class="card"><div class="n">{summary.get('console_errors', 0)}</div><div class="l">Console errors</div></div>
  <div class="card"><div class="n">{summary.get('page_errors', 0)}</div><div class="l">Page errors</div></div>
</div>
{section("Failed Requests", failed, ["status", "method", "url"])}
{section("Console Errors", data.get("console_errors", []), ["type", "text"])}
{section("Page Errors", [{"text": e} for e in data.get("page_errors", [])], ["text"])}
{section("Slowest Requests", slowest, ["timing_ms", "status", "url"])}
{sec_section}
{notes_section}
<footer>Generated by Web-Site-OSINT devtools-auto.py. See SCOPE.md for what this tool can and cannot tell you.</footer>
</body>
</html>"""

    with open(args.output, "w") as f:
        f.write(html_doc)
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
