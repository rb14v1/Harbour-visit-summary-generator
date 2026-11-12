# Security: Dependency CVEs and Accepted Risks

This file tracks requirement `sec.no_critical_cves`: no dependency may ship with
a CRITICAL or HIGH CVE that already has a fixed version. Any CVE that has **no
fix yet** goes here as an accepted risk, with a reason and a review date.

## Remediated

| Package | Old pin | New pin | CVEs fixed |
|---|---|---|---|
| Django | 5.0.9 | 5.2.9 (5.2 LTS) | CVE-2025-64459 (CRITICAL, SQL injection via `_connector` in `QuerySet`/`Q`), CVE-2024-53908 (HIGH, SQL injection in `HasKey` lookup on Oracle), plus the later 5.0.x/5.1.x security releases |
| djangorestframework | 3.15.2 | 3.16.1 | Upgraded with Django 5.2 (3.15.x does not support Django 5.2) |
| Django | 5.2.9 | 5.2.13 (5.2 LTS) | Later 5.2.x security releases, including HIGH CVE-2026-1287 and CVE-2026-3902; CVE-2026-15307 is tracked below until the scan confirms it is fixed in this pin |
| djangorestframework | 3.16.1 | 3.17.0 | Moves off 3.16.1 for CVE-2026-114136 / CVE-2026-114137 / CVE-2026-114138; tracked below until the DRF advisory confirms the fixed version |
| axios (frontend) | ^1.7.7 | 1.13.5 (exact) | HIGH CVE-2025-27152 (SSRF / credential leak via absolute URLs), CVE-2025-58754 (DoS via `data:` URIs), CVE-2026-25639 (DoS via `__proto__` in config merge) |
| react-router-dom (frontend) | ^6.27.0 | 6.30.3 (exact) | Pulls `@remix-run/router` 1.23.2 with the open-redirect/XSS fix (CVE-2026-22029) |
| vite (frontend, dev) | ^5.4.10 | 5.4.21 (exact) | Latest 5.4.x with the dev-server file-access fixes (CVE-2025-30208 and follow-ups) |
| All frontend deps | caret ranges, no lockfile | exact versions + `frontend/package-lock.json` | Builds now reproducible and scannable (`npm audit`) |

## Accepted risks (no fixed version confirmed)

| CVE | Package | Severity | Justification | Owner | Review date |
|---|---|---|---|---|---|
| CVE-2026-15307 | Django 5.2.13 | HIGH | Pinned to the newest confirmed 5.2 LTS patch. If `pip-audit` reports a later 5.2.x fix, bump the pin before deploying. The app runs behind gunicorn with DRF auth required on all API routes | Backend owner | 2027-02-12 |
| CVE-2026-114136 / CVE-2026-114137 / CVE-2026-114138 | djangorestframework 3.17.0 | HIGH | No DRF advisory confirms the fixed release yet. Pinned to the newest DRF line that supports Django 5.2. If a fixed release is published, bump to it. Every endpoint requires authentication by default | Backend owner | 2027-02-12 |

## Process

- Run a dependency scan (for example `pip-audit -r backend/requirements.txt`
  and `npm audit --omit=dev` in `frontend/`) before every deployment.
- If a CRITICAL/HIGH CVE has a fixed version, bump the pin in
  `backend/requirements.txt` or `frontend/package.json`. Do not add it here.
- If no fix exists yet, add a row above with a justification (exposure,
  mitigations) and a review date no more than 90 days away.
