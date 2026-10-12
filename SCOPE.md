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
