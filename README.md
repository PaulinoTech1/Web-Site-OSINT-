# Web-Site-OSINT

Scriptable DevTools inspection for websites. Automates what you'd manually
check in Chrome DevTools: network requests, console errors, page errors.

**This is a defensive inspection aid, not an offensive tool.** It loads pages
the way a normal visitor's browser would and reports what it observes. It does
not scan, exploit, or bypass anything. See [SCOPE.md](SCOPE.md) for the full
scope statement, including what the tool can and cannot tell you and the
permissions required before use.

## Quick start (uv)

**Install uv first** (one time):

| OS | Command |
|----|---------|
| Windows (PowerShell) | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` |
| macOS / Linux | `curl -LsSf https://astral.sh/uv/install.sh | sh` |

After installing, restart your terminal (or run `refreshenv` on Windows) so
`uv` is on your PATH. Verify with `uv --version`.

Then:

```
uv sync
uv run playwright install chromium
uv run devtools-auto.py https://example.com
uv run view-report.py devtools-report.json
```

Open `report.html` in any browser for a clean, readable summary.

> **Windows note:** all `uv` commands above work identically in PowerShell
> once uv is installed. If `uv run playwright install chromium` fails on
> missing system libraries, run it from an elevated PowerShell so Playwright
> can install the browser dependencies.

### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `uv: The term 'uv' is not recognized` (PowerShell) | uv is not installed, or the terminal was not restarted after install | Run the Windows install command above, then close and reopen PowerShell |
| `playwright install` hangs or fails | Missing system libraries (Linux) or blocked download | Linux: `sudo uv run playwright install-deps`; then retry. Check firewall/proxy if the download itself fails |
| `ERR_TUNNEL_CONNECTION_FAILED` in Chromium | Browser cannot reach the network through the environment's egress proxy | This tool needs direct network access from the browser. Run it on a normal workstation, not inside a sandboxed VM with proxy-only egress. See SCOPE.md |
| `view-report.py: Cannot read devtools-report.json` | The inspection step failed or wrote to a different path | Check that `devtools-auto.py` completed successfully first |
| `irm https://astral.sh/uv/install.ps1` fails or returns empty | Ad/script blocker (e.g. uBlock Origin) interfering with the download | Temporarily disable the blocker or whitelist `astral.sh`, then re-run the install command. Re-enable it after. |

### Why uv, and why this stays small

This project uses `uv` instead of `pip` as a deliberate speed and scope
decision. `uv sync` resolves and installs from `pyproject.toml` in seconds,
into a project-local `.venv`. Nothing touches system Python.

The dependency list is exactly one package: `playwright`. That's the only
thing this project needs. `view-report.py` is stdlib-only. There is no web
framework, no ORM, no test runner, no linter config. If a future addition
can't justify its install time and its place in the dependency tree, it
doesn't belong here.

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
| `--screenshot FILE` | Screenshot path (default `devtools-screenshot.png`) |

Output:
- `devtools-report.json` — summary, failed requests, console errors, slowest requests, security headers
- `devtools-screenshot.png` — full-page viewport screenshot

Exit code is 0 when no failed requests, console errors, or page errors are found.

## Tests

Stdlib only, no test runner dependency:

```
python -m unittest discover -s tests -v
```

CI runs the suite on every push via `.github/workflows/ci.yml`. Browser
behavior is not tested in CI; the unit tests cover the pure helpers
(`parse_content_length`) that previously shipped a real bug.

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
