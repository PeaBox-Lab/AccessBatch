# AccessBatch

> Accessibility testing in batches. Evidence developers can act on.

AccessBatch is an open-source website accessibility scanner designed for small development teams.

Give AccessBatch a website URL and it can crawl the site, render pages in Chromium, run automated accessibility checks, capture screenshots, and package the findings into developer-friendly evidence bundles.

## Why AccessBatch?

Accessibility testing often becomes a collection of one-off browser checks, spreadsheets, screenshots, and manually assembled evidence.

AccessBatch makes the automated part repeatable:

URL → Crawl → Render → Scan → Capture → Report → Evidence Bundle

## Core Features

- Crawl same-origin website pages
- Set a maximum number of pages per scan
- Render pages using Playwright and Chromium
- Run axe-core accessibility checks
- Target WCAG A/AA tagged automated rules
- Capture full-page screenshots
- Record DOM selectors and failing HTML
- Generate JSON findings
- Generate standalone HTML reports
- Package evidence into downloadable ZIP bundles
- Maintain local scan history with SQLite
- Run through a lightweight FastAPI web interface

## Important

AccessBatch provides automated accessibility findings and evidence.

Automated testing cannot identify every accessibility issue, so AccessBatch results should not be treated as proof or certification of WCAG conformance.
