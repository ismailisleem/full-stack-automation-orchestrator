from __future__ import annotations

import asyncio
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "docs" / "assets" / "walkthrough"


async def main(report_root: Path) -> None:
    from playwright.async_api import async_playwright

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        await capture(page, report_root / "index.html", "portfolio-dashboard.png")
        await capture(page, report_root / "reports.html", "reports-gallery.png")
        await capture(page, report_root / "compare.html", "compare-runs.png")
        run_pages = sorted((report_root / "runs").glob("*/index.html"))
        if run_pages:
            await capture(page, run_pages[-1], "run-overview.png")
            detail_pages = sorted(run_pages[-1].parent.glob("tests/*.html"))
            if detail_pages:
                await capture(page, detail_pages[0], "test-details.png")
        await browser.close()


async def capture(page, html_path: Path, filename: str) -> None:
    if not html_path.exists():
        raise FileNotFoundError(html_path)
    await page.goto(html_path.as_uri(), wait_until="networkidle")
    await page.screenshot(path=ASSET_DIR / filename, full_page=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--report-root", default="reports/orchestrator")
    args = parser.parse_args()
    asyncio.run(main((ROOT / args.report_root).resolve()))
