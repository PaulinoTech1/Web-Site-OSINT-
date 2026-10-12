# Web-Site-OSINT

Scriptable DevTools inspection for websites. Automates what you'd manually
check in Chrome DevTools: network requests, console errors, page errors.

## devtools-auto.py

Captures network traffic, console output, and uncaught page errors for any URL,
then writes a JSON report and screenshot.

```
pip install playwright
playwright install chromium
python3 devtools-auto.py https://example.com
```

Options:

| Flag | Purpose |
|------|---------|
| `--headed` | Show the browser window while it runs |
| `--wait MS` | Milliseconds to wait after page load (default 3000) |
| `--out FILE` | Report path (default `devtools-report.json`) |

Output:
- `devtools-report.json` — summary, failed requests, console errors, slowest requests
- `devtools-screenshot.png` — viewport screenshot

Exit code is 0 when no failed requests, console errors, or page errors are found.
