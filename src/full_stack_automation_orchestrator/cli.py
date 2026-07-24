from __future__ import annotations

import argparse
import sys
from pathlib import Path

from automation_core.reporting import combine_report_portfolios, open_report

from full_stack_automation_orchestrator import __version__
from full_stack_automation_orchestrator.adapters import RunPlan, SubprocessFrameworkAdapter
from full_stack_automation_orchestrator.config import load_orchestrator_config
from full_stack_automation_orchestrator.journey import Journey, JourneyRunner, JourneyStep
from full_stack_automation_orchestrator.preflight import run_config_preflight
from full_stack_automation_orchestrator.reporting import generate_orchestrator_report
from full_stack_automation_orchestrator.samples import run_sample


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        return _doctor(args)
    if args.command == "run-sample":
        return _run_sample(args)
    if args.command == "run-plan":
        return _run_plan(args)
    if args.command == "combine-reports":
        return _combine_reports(args)
    parser.print_help()
    return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="full-stack-orchestrator")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Validate orchestrator config and target readiness.")
    doctor.add_argument("--config", default="config/orchestrator.yaml")

    sample = subparsers.add_parser("run-sample", help="Run a built-in cross-platform sample journey.")
    sample.add_argument("sample", choices=["api-web", "api-mobile", "full", "all"])
    sample.add_argument("--output", default="reports/orchestrator")
    sample.add_argument("--open", action="store_true", dest="open_report")

    run_plan = subparsers.add_parser("run-plan", help="Run enabled framework targets from config as isolated phases.")
    run_plan.add_argument("--config", default="config/orchestrator.yaml")
    run_plan.add_argument("--target", action="append", default=[])
    run_plan.add_argument("--output", default=None)
    run_plan.add_argument("--open", action="store_true", dest="open_report")

    combine = subparsers.add_parser("combine-reports", help="Build one portfolio from framework report roots.")
    combine.add_argument("--source", action="append", required=True)
    combine.add_argument("--output", required=True)
    combine.add_argument("--open", action="store_true", dest="open_report")
    return parser


def _doctor(args: argparse.Namespace) -> int:
    config = load_orchestrator_config(args.config)
    result = run_config_preflight(config, base_dir=Path(args.config).resolve().parent.parent)
    for check in result.checks:
        print(f"{check.status.upper():7} {check.name} - {check.message}")
    return 0 if result.ok else 1


def _run_sample(args: argparse.Namespace) -> int:
    sample = run_sample(args.sample, output_dir=args.output)
    print(f"Portfolio: {sample.report.portfolio_index}")
    print(f"Run report: {sample.report.run_index}")
    if args.open_report:
        open_report(sample.report.portfolio_index)
    return 0 if all(result.passed for result in sample.results) else 1


def _run_plan(args: argparse.Namespace) -> int:
    config = load_orchestrator_config(args.config)
    preflight = run_config_preflight(config, base_dir=Path(args.config).resolve().parent.parent)
    if not preflight.ok:
        for failure in preflight.failures:
            print(f"FAILED {failure.name} - {failure.message}", file=sys.stderr)
        return 1

    selected = set(args.target)
    targets = [
        target for target in config.targets.values() if target.enabled and (not selected or target.name in selected)
    ]
    adapters = {platform: SubprocessFrameworkAdapter(platform) for platform in {target.platform for target in targets}}

    def make_step(target):
        def action(context):
            adapter = context.adapter(target.platform)
            run_result = adapter.run_plan(
                RunPlan(
                    name=target.name,
                    command=target.command,
                    cwd=target.repo_path,
                    env=target.env,
                    timeout_seconds=target.timeout_seconds,
                    report_path=Path(target.repo_path) / target.report_root / "index.html"
                    if target.report_root
                    else None,
                    metadata=target.metadata,
                ),
                context,
            )
            return run_result.to_step_output()

        return JourneyStep(target.name, action, platform=target.platform, metadata=target.metadata)

    journey = Journey(
        journey_id="configured-framework-plan",
        name="Configured framework plan",
        suite="configured",
        domain="cross-platform",
        environment=config.environment,
        steps=[make_step(target) for target in targets],
    )
    runner = JourneyRunner(config=config, adapters=adapters, artifacts_dir=".tmp/orchestrator-plan-artifacts")
    result = runner.run(journey)
    output = args.output or config.reporting.output_dir
    report = generate_orchestrator_report(
        result,
        output,
        project_name=config.project_name,
        history_dir=config.reporting.history_dir,
        safe_share=config.reporting.safe_share,
        update_history_file=config.reporting.update_history_file,
    )
    print(f"Portfolio: {report.portfolio_index}")
    print(f"Run report: {report.run_index}")
    if args.open_report or config.reporting.open_report:
        open_report(report.portfolio_index)
    return 0 if result.passed else 1


def _combine_reports(args: argparse.Namespace) -> int:
    path = combine_report_portfolios(args.source, args.output)
    print(f"Combined portfolio: {path}")
    if args.open_report:
        open_report(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
