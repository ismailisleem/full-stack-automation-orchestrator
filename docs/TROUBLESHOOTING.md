# Troubleshooting

## `automation_core` Cannot Be Imported

Install the orchestrator in a virtual environment:

```bash
python -m pip install -e ".[dev]"
```

For configured framework targets, use each framework's own virtual environment in `config/orchestrator.yaml`, for example `.venv/bin/python`.

## `full_stack_automation_orchestrator` Cannot Be Imported After Editable Install

If the repository lives under a path with spaces and your Python environment does not process the
editable-install `.pth` file correctly, run local CLI validation with:

```bash
PYTHONPATH=src full-stack-orchestrator run-sample all --output reports/orchestrator
```

Non-editable installs from a wheel or Git tag are not affected because the package is installed into
site-packages directly.

## A Configured Target Fails Before Tests Start

Run:

```bash
full-stack-orchestrator doctor --config config/orchestrator.yaml
```

Check:

- `repo_path` points to an existing framework repository.
- `command` uses an executable available from that repository.
- `required_env` values are set when the target needs secrets or environment-specific configuration.

## Web Target Cannot Launch A Browser

The orchestrator does not install browser dependencies. Run the Web framework setup from `web-automation-framework`, including Playwright browser installation, then rerun the orchestrator target.

For report visual QA and screenshots, use Playwright bundled Chromium or another non-system-Chrome renderer.

## Mobile Target Cannot Find A Device

The orchestrator does not start Appium or create simulators. Validate the Mobile framework first:

```bash
cd ../mobile-automation-framework
.venv/bin/python framework.py doctor
```

Use device-free helper targets for CI-style checks, and use Android/iOS profile targets only when Appium and the target device or simulator are ready.

## Reports Are Generated But Old Runs Remain

That is expected. The automation-core product report retains timestamped run folders and rebuilds the portfolio dashboard over history. Remove old reports manually only when you intentionally want a clean local workspace.

## A Report Opens The Wrong Browser

The orchestrator does not force a browser for report opening. Use `--output` to generate reports and open the HTML manually, or keep `open_report: false` in config for CI and server environments.
