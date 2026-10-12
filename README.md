# Web-Site-OSINT

Scriptable DevTools inspection for websites. Automates what you'd manually
check in Chrome DevTools: network requests, console errors, page errors.

**This is a defensive inspection aid, not an offensive tool.** It loads pages
the way a normal visitor's browser would and reports what it observes. It does
not scan, exploit, or bypass anything. See [SCOPE.md](SCOPE.md) for the full
scope statement, including what the tool can and cannot tell you and the
permissions required before use.

## Quick start

```
pip install playwright
playwright install chromium
python3 devtools-auto.py https://example.com
python3 view-report.py devtools-report.json
```

Open `report.html` in any browser for a clean, readable summary.

## Tools

| Script | Purpose |
|--------|---------|
| `devtools-auto.py` | Inspect a URL: network, console, page errors → JSON report + screenshot |
| `view-report.py` | Convert the JSON report into a self-contained HTML page |

### devtools-auto.py options

| Flag | Purpose |
|------|---------|
| `--headed` | Show the browser window while it runs |
| `--wait MS` | Milliseconds to wait after page load (default 3000) |
| `--out FILE` | Report path (default `devtools-report.json`) |

Output:
- `devtools-report.json` — summary, failed requests, console errors, slowest requests
- `devtools-screenshot.png` — viewport screenshot

Exit code is 0 when no failed requests, console errors, or page errors are found.

### view-report.py options

```
python3 view-report.py devtools-report.json -o report.html
```

Produces a single self-contained HTML file. No server needed, no dependencies.
Green "CLEAN" badge when nothing failed; red "ISSUES FOUND" otherwise.

## Before you use this

Read [SCOPE.md](SCOPE.md). In short:

- **Your own sites:** go ahead, that's what this is for.
- **Authorized assessments:** stay within your authorization scope.
- **Everything else:** get permission first.
- **This is not a penetration testing toolkit.** It is a poor fit for offensive
  reconnaissance by design.
