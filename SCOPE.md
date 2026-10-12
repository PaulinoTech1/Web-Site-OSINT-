# Scope: What This Tool Is and Is Not

## What this is

Web-Site-OSINT is a **defensive website inspection aid**. It loads a public
web page in a real browser and reports what that page does: what it requests,
what errors it throws, what it looks like. Think of it as automating the
manual DevTools checks a developer or security reviewer would do by hand.

## What this is NOT

**This is not a hacker tool. This is not Kali Linux. This is not for
offensive reconnaissance.**

This tool is a poor fit for offensive work, by design:

- It does not scan ports, enumerate services, or fingerprint infrastructure.
- It does not test for vulnerabilities, inject payloads, or attempt exploitation.
- It does not bypass authentication, brute-force credentials, or evade bot detection.
- It does not perform subdomain enumeration, directory busting, or parameter fuzzing.
- It loads pages the way a normal visitor's browser would. That is all.

If you are looking for penetration testing tooling, this repository will
disappoint you. That is intentional.

## What the tool CAN tell you

When pointed at a publicly accessible URL, the tool observes:

| Observation | Source | Use case |
|-------------|--------|----------|
| HTTP requests the page makes | Network tab | Spot unexpected third-party calls, trackers, or data exfiltration |
| Failed requests (4xx/5xx) | Network tab | Find broken assets, missing resources |
| JavaScript console errors | Console tab | Catch runtime bugs before users do |
| Uncaught page exceptions | Page error events | Find crashes that don't surface in the console |
| Slowest resources | Request timing | Identify performance bottlenecks |
| Rendered page title | DOM | Confirm the right page loaded |
| Viewport screenshot | Rendering | Visual regression checks |

## What the tool CANNOT tell you

| Limitation | Why |
|------------|-----|
| Server-side logic | The tool only sees what the browser receives. Backend code, database queries, and API internals are invisible. |
| Authenticated content | Without credentials, only public pages are visible. The tool does not bypass logins. |
| What other users see | Personalized or geo-targeted content may differ per visitor. |
| Whether a site is "secure" | Absence of console errors is not a security assessment. This tool is not a vulnerability scanner. |
| Historical state | It captures the page as it is right now, not what it was yesterday. |
| Mobile vs desktop differences | Unless configured, it uses a desktop viewport. Responsive issues need separate runs. |
| Request/response bodies | Not captured. The tool records metadata (URL, status, headers, timing), not payloads. |
| WebSocket frames | Not captured. Long-lived connections are invisible beyond the initial handshake. |
| Certificate details | Not extracted. Use `openssl s_client` or certificate transparency logs for cert analysis. |
| Service worker internals | Traffic served from cache by a service worker may not appear as network requests. |

## A note on the name

The repository is called "Web-Site-OSINT" but the tool performs none of the
traditional OSINT primitives: no WHOIS lookups, no DNS enumeration, no
certificate transparency searches, no subdomain discovery, no technology
fingerprinting beyond incidental request URLs, no historical archive queries.

The name reflects the original intent (observing what a site reveals about
itself to a visitor), not the full OSINT discipline. If you need those
primitives, use dedicated tools: `whois`, `dig`, crt.sh, the Wayback Machine,
Wappalyzer. This tool answers one question: "what does this page do when it
loads?" Everything else is out of scope.

## How to read the output

A report from this tool is the **start** of an investigation, not the end of
one. Treat every finding as the initiation of a deeper, approved OSINT dive:

- A clean report does not mean a site is secure. It means nothing failed
  during one automated page load.
- A failed request does not mean a vulnerability. It means an asset didn't
  load; the cause could be a typo, a deleted file, or a CDN hiccup.
- A console error does not mean exploitable. It means JavaScript threw;
  triage it like any other bug report.

The tool was developed and tested primarily in a Windows environment. That
configuration is **not conclusive**: browser behavior, rendering, and network
conditions vary across operating systems, and a single run captures one
moment in time. Do not treat one report as a final assessment. Corroborate
findings manually before acting on them, and stay within the authorization
scope described above.

## Environment requirements and known limitations

The tool needs a real Chromium browser with **direct network access**.
It does not work in every environment:

| Requirement | Detail |
|-------------|--------|
| Chromium | Installed via `playwright install chromium`, or pointed at a system Chromium |
| Direct egress | The browser must reach the target site itself. Environments that force traffic through an authenticated MITM egress proxy may block Chromium's tunnel setup (`ERR_TUNNEL_CONNECTION_FAILED`) even when `curl` works fine. Verified 2026-10-12: the tool cannot run inside sandboxed VMs with proxy-only egress. Run it on a normal workstation or server instead. |
| Display (optional) | Headless by default. `--headed` needs a display or Xvfb. |
| Disk | ~170MB for the Chromium download, plus the Python venv |

**This is a local workstation tool, not a cloud service.** It was designed to
run on a developer's machine, not inside locked-down containers, CI runners
with restricted egress, or serverless functions. If the browser cannot reach
the network, the tool fails fast with a connection error. That is the correct
behavior; do not work around it by disabling certificate validation or
proxying through untrusted intermediaries.

## Permissions required before use

**You must have permission to inspect the target site.** Specifically:

1. **Your own sites:** No additional permission needed. This is the primary use case: checking your own deployments for broken assets, JS errors, or unexpected third-party requests.

2. **Sites you are authorized to review:** If a client, employer, or bug bounty program has authorized you to assess a site, stay within the scope of that authorization. This tool only performs passive observation (loading pages as a normal visitor), which is the least intrusive form of assessment, but authorization still matters.

3. **Third-party sites without authorization:** Do not use this tool for systematic inspection of sites you have no relationship with. Loading a single public page is what every visitor does, but automated repeated inspection without permission is unwanted traffic at best.

**When in doubt, ask first.** The tool is passive, but courtesy and authorization are not optional.

## Intended users

- Developers verifying their own deployments
- Security reviewers doing defensive assessment of sites they are authorized to check
- QA engineers automating visual and console-error regression checks
- Anyone who wants to know "what does this page actually load?" for a site they have permission to inspect

## Not intended for

- Penetration testers looking for an attack toolkit (use purpose-built tools with proper authorization)
- Anyone conducting reconnaissance without permission
- Automated scraping at scale (this tool loads full pages in a real browser; it is slow and obvious by design)

## Scope boundaries: what this will never become

To keep the project honest about its size and purpose, the following are
explicitly out of scope and will not be added:

- **No vulnerability scanning.** No payload injection, no CVE checks, no misconfiguration detection. That is a different tool.
- **No credential handling.** No login automation, no session management, no cookie jars. Public pages only.
- **No stealth.** No user-agent rotation, no proxy chains, no bot-evasion. The tool identifies as an automated browser.
- **No bulk operation.** No sitemap crawling, no multi-target sweeps, no scheduling. One URL, one run.
- **No server component.** No API, no dashboard, no database. Scripts that run locally and exit.

Each of these would expand the attack surface of the tool itself and blur
the line this project draws between defensive inspection and offensive
capability. The line stays where it is.
