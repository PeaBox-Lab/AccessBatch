# AccessBatch

AccessBatch is a small-team website accessibility batch scanner. It crawls same-origin pages, renders each page in Chromium with Playwright, runs axe-core WCAG-tagged automated checks, captures full-page screenshots, and produces a developer evidence bundle.

## MVP
- Same-origin crawl, with 1–100 page limit
- Playwright Chromium rendering
- axe-core automated WCAG A/AA tagged checks
- Full-page PNG evidence
- JSON findings
- Standalone HTML report
- ZIP issue bundle
- FastAPI web UI and scan-status API
- SQLite scan history

## Important
Automated accessibility checks detect only some accessibility problems. AccessBatch reports findings as **automated evidence**, not a certificate of WCAG conformance.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

On Windows PowerShell, activation is optional:

```powershell
py -m venv C:\venvs\accessbatch
C:\venvs\accessbatch\Scripts\python.exe -m pip install -r requirements.txt
C:\venvs\accessbatch\Scripts\python.exe -m playwright install chromium
C:\venvs\accessbatch\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the local Uvicorn address shown in the console.

## GitHub direction
Suggested repository metadata:
- Name: `accessbatch`
- Description: `Batch website accessibility scans with Playwright, axe-core, screenshots and developer evidence bundles.`
- Topics: `accessibility`, `wcag`, `axe-core`, `playwright`, `fastapi`, `a11y`, `website-audit`, `python`
- License suggestion: Apache-2.0 for an open core, or keep private until the hosted model is decided.

## Next product increments
1. Sitemap.xml discovery and include/exclude path rules
2. Baseline/suppression file for accepted findings
3. Duplicate finding clustering and issue fingerprints
4. Per-rule evidence pages with cropped element screenshot
5. CI exit thresholds by impact
6. Authenticated scans/save login-state
7. Scheduled hosted scans and regression history
8. SARIF/GitHub Issues/Jira export
9. Manual-review checklist alongside automated findings
