# Security: Dependency CVEs and Accepted Risks

This file tracks requirement `sec.no_critical_cves`: no dependency may ship with
a CRITICAL or HIGH CVE that already has a fixed version. Any CVE that has **no
fix yet** goes here as an accepted risk, with a reason and a review date.

## Remediated

| Package | Old pin | New pin | CVEs fixed |
|---|---|---|---|
| Django | 5.0.9 | 5.2.9 (5.2 LTS) | CVE-2025-64459 (CRITICAL, SQL injection via `_connector` in `QuerySet`/`Q`), CVE-2024-53908 (HIGH, SQL injection in `HasKey` lookup on Oracle), plus the later 5.0.x/5.1.x security releases |
| djangorestframework | 3.15.2 | 3.16.1 | Upgraded with Django 5.2 (3.15.x does not support Django 5.2). Fixes for CVE-2026-114136 / CVE-2026-114137 / CVE-2026-114138 must be confirmed against the DRF advisory; if a later DRF release holds the fix, bump this pin to it |

## Accepted risks (no fixed version available)

| CVE | Package | Severity | Justification | Owner | Review date |
|---|---|---|---|---|---|
| _None currently_ | | | | | 2027-02-12 |

## Process

- Run a dependency scan (for example `pip-audit -r backend/requirements.txt`)
  before every deployment.
- If a CRITICAL/HIGH CVE has a fixed version, bump the pin in
  `backend/requirements.txt`. Do not add it here.
- If no fix exists yet, add a row above with a justification (exposure,
  mitigations) and a review date no more than 90 days away.
