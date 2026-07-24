from __future__ import annotations

from full_stack_automation_orchestrator import Journey, JourneyRunner, JourneyStep, RetryPolicy, StepOutput


def test_journey_shares_state_between_platform_steps(tmp_path):
    def api_step(context):
        context.state.set("order.id", "ORD-7")
        return StepOutput(metadata={"platform": "api"})

    def web_step(context):
        return StepOutput(data={"order_id": context.state.require("order.id")}, metadata={"platform": "web"})

    journey = Journey(
        name="state handoff",
        steps=[
            JourneyStep("api", api_step, platform="api"),
            JourneyStep("web", web_step, platform="web", depends_on=("api",)),
        ],
    )

    result = JourneyRunner(artifacts_dir=str(tmp_path)).run(journey)

    assert result.passed
    assert result.steps[1].data == {"order_id": "ORD-7"}


def test_journey_records_successful_retry(tmp_path):
    attempts = {"count": 0}

    def flaky_step(context):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("not ready")
        return StepOutput(data={"ready": True})

    journey = Journey(
        name="retry",
        steps=[JourneyStep("mobile confirmation", flaky_step, platform="mobile", retry=RetryPolicy(attempts=2))],
    )

    result = JourneyRunner(artifacts_dir=str(tmp_path)).run(journey)

    assert result.passed
    assert result.steps[0].attempts == 2
    assert result.steps[0].retry_records[0].reason == "not ready"


def test_journey_fail_fast_skips_remaining_steps(tmp_path):
    def failed(context):
        raise AssertionError("boom")

    journey = Journey(
        name="fail fast",
        steps=[
            JourneyStep("api", failed, platform="api"),
            JourneyStep("web", lambda context: StepOutput(), platform="web"),
        ],
    )

    result = JourneyRunner(artifacts_dir=str(tmp_path)).run(journey)

    assert result.status == "failed"
    assert [step.status for step in result.steps] == ["failed", "skipped"]
