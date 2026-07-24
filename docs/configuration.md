# Configuration

The default config lives in `config/orchestrator.yaml`.

```yaml
project_name: Full-Stack Automation Orchestrator
environment: local
fail_fast: true

reporting:
  output_dir: reports/orchestrator
  history_dir: reports/orchestrator/history
  safe_share: true
  update_history_file: true
  open_report: false

targets:
  api-smoke:
    platform: api
    repo_path: ../api-automation-framework
    command: ["python", "framework.py", "run", "--env", "mock", "--smoke", "--no-open-report"]
```

## Target Fields

- `platform`: `api`, `web`, or `mobile`.
- `repo_path`: path to the framework repository.
- `command`: command executed from `repo_path`.
- `env`: extra environment variables for that phase.
- `required_env`: environment variables that must exist before the target runs.
- `timeout_seconds`: phase timeout.
- `report_root`: framework report root used as an artifact reference.
- `metadata`: extra labels shown in the orchestrator report.
