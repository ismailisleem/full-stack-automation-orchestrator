# Reporting

The orchestrator reports through `automation-core`.

Each run writes:

- `reports/orchestrator/index.html`: portfolio dashboard for all retained runs.
- `reports/orchestrator/reports.html`: report gallery.
- `reports/orchestrator/compare.html`: compare selected runs.
- `reports/orchestrator/runs/<timestamp>-<run-id>/index.html`: current run overview.
- `reports/orchestrator/runs/<timestamp>-<run-id>/tests/`: per-journey details.
- `reports/orchestrator/runs/<timestamp>-<run-id>/exports/`: CSV, XLSX, DOCX, SVG, JSON bundle, and share manifest.

The orchestrator does not delete old runs. Every generated run gets a timestamped folder, then the portfolio pages are rebuilt over retained history.

## Report Data

The neutral `report-data.json` sidecar is the best validation target for automated checks. The HTML is for people; the JSON sidecar is for assertions and integrations.

## Visual QA

When reviewing generated HTML, use Playwright bundled Chromium or another non-system-Chrome renderer. Check both desktop and mobile widths for:

- Horizontal page overflow.
- Clipped table headings or run IDs.
- Cards that overlap or resize unexpectedly.
- Missing artifacts or broken links.
