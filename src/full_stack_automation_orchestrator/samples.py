from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from full_stack_automation_orchestrator.adapters import AdapterRegistry, FunctionAdapter
from full_stack_automation_orchestrator.config import OrchestratorConfig
from full_stack_automation_orchestrator.journey import Journey, JourneyRunner, JourneyStep
from full_stack_automation_orchestrator.models import ArtifactRef, JourneyResult, RetryPolicy, StepOutput
from full_stack_automation_orchestrator.reporting import OrchestratorReportPaths, generate_orchestrator_report
from full_stack_automation_orchestrator.state import ScenarioState


@dataclass(frozen=True)
class SampleRun:
    results: tuple[JourneyResult, ...]
    report: OrchestratorReportPaths


def run_sample(sample: str, *, output_dir: str | Path = "reports/orchestrator") -> SampleRun:
    output_path = Path(output_dir)
    journeys = sample_journeys(sample)
    results: list[JourneyResult] = []
    for journey in journeys:
        runner = _sample_runner(output_path / "source-artifacts" / journey.resolved_id())
        results.append(runner.run(journey))
    report = generate_orchestrator_report(
        tuple(results),
        output_path,
        project_name="Full-Stack Automation Orchestrator Samples",
        history_dir=output_path / "history",
    )
    return SampleRun(tuple(results), report)


def sample_journeys(sample: str) -> tuple[Journey, ...]:
    normalized = sample.strip().lower().replace("_", "-")
    if normalized == "api-web":
        return (api_web_journey(),)
    if normalized == "api-mobile":
        return (api_mobile_journey(),)
    if normalized in {"full", "full-journey", "all-platforms"}:
        return (full_stack_journey(),)
    if normalized == "all":
        return (api_web_journey(), api_mobile_journey(), full_stack_journey())
    raise ValueError("Unknown sample. Use api-web, api-mobile, full, or all.")


def api_web_journey() -> Journey:
    return Journey(
        journey_id="api-web-order",
        name="API creates an order and Web completes checkout",
        suite="samples",
        domain="api-web",
        steps=[
            JourneyStep("Create order through API", _api_create_order, platform="api"),
            JourneyStep(
                "Checkout order through Web",
                _web_checkout_order,
                platform="web",
                depends_on=("Create order through API",),
            ),
            JourneyStep(
                "Verify API order status",
                _api_verify_order_completed,
                platform="api",
                depends_on=("Checkout order through Web",),
            ),
        ],
        metadata={"component": "checkout"},
    )


def api_mobile_journey() -> Journey:
    return Journey(
        journey_id="api-mobile-order",
        name="API creates an order and Mobile verifies confirmation",
        suite="samples",
        domain="api-mobile",
        steps=[
            JourneyStep("Create order through API", _api_create_order, platform="api"),
            JourneyStep(
                "Confirm order on Mobile",
                _mobile_confirm_order,
                platform="mobile",
                depends_on=("Create order through API",),
            ),
            JourneyStep(
                "Verify mobile confirmation through API",
                _api_verify_mobile_confirmation,
                platform="api",
                depends_on=("Confirm order on Mobile",),
            ),
        ],
        metadata={"component": "mobile-confirmation"},
    )


def full_stack_journey() -> Journey:
    return Journey(
        journey_id="full-stack-checkout",
        name="Full-stack checkout across API, Web, and Mobile",
        suite="samples",
        domain="full-stack",
        steps=[
            JourneyStep("Seed customer through API", _api_seed_customer, platform="api"),
            JourneyStep(
                "Build cart through Web", _web_build_cart, platform="web", depends_on=("Seed customer through API",)
            ),
            JourneyStep(
                "Authorize payment through API",
                _api_authorize_payment,
                platform="api",
                depends_on=("Build cart through Web",),
            ),
            JourneyStep(
                "Observe mobile push confirmation",
                _mobile_push_confirmation,
                platform="mobile",
                retry=RetryPolicy(attempts=2),
                depends_on=("Authorize payment through API",),
                metadata={"retry_demo": True},
            ),
        ],
        metadata={"component": "checkout", "risk_area": "cross-platform handoff"},
    )


def _sample_runner(artifacts_dir: Path) -> JourneyRunner:
    adapters = AdapterRegistry(
        {
            "api": FunctionAdapter("api", actions={}),
            "web": FunctionAdapter("web", actions={}),
            "mobile": FunctionAdapter("mobile", actions={}),
        }
    )
    return JourneyRunner(
        config=OrchestratorConfig(
            project_name="Full-Stack Automation Orchestrator Samples",
            environment="local",
            metadata={"sample": True},
        ),
        adapters=adapters,
        state=ScenarioState(),
        artifacts_dir=str(artifacts_dir),
    )


def _api_create_order(context) -> StepOutput:
    order = {"id": "ORD-1001", "status": "created", "total": 129.99}
    context.state.update({"order.id": order["id"], "order.status": order["status"], "order.total": order["total"]})
    artifact = _write_json_artifact(context, "api-create-order.json", {"response": order})
    return StepOutput(
        data={"order_id": order["id"], "status_code": 201},
        metadata={"platform": "api", "status_code": 201, "latency_ms": 42},
        artifacts=(artifact,),
    )


def _web_checkout_order(context) -> StepOutput:
    order_id = context.state.require("order.id")
    context.state.set("order.status", "completed")
    artifact = _write_json_artifact(context, "web-checkout.json", {"order_id": order_id, "screen": "checkout-complete"})
    return StepOutput(
        data={"order_id": order_id, "message": "Thank you for your order"},
        metadata={"platform": "web", "browser": "chromium", "viewport": "1440x900"},
        artifacts=(artifact,),
    )


def _api_verify_order_completed(context) -> StepOutput:
    status = context.state.require("order.status")
    if status != "completed":
        return StepOutput(status="failed", data={"expected": "completed", "actual": status})
    return StepOutput(
        data={"order_id": context.state.require("order.id"), "status": status}, metadata={"platform": "api"}
    )


def _mobile_confirm_order(context) -> StepOutput:
    order_id = context.state.require("order.id")
    context.state.set("mobile.confirmed", True)
    artifact = _write_json_artifact(context, "mobile-confirmation.json", {"order_id": order_id, "confirmed": True})
    return StepOutput(
        data={"order_id": order_id, "confirmed": True},
        metadata={"platform": "mobile", "device_name": "sample-simulator", "context": "native"},
        artifacts=(artifact,),
    )


def _api_verify_mobile_confirmation(context) -> StepOutput:
    return StepOutput(
        data={"confirmed": context.state.require("mobile.confirmed")},
        metadata={"platform": "api", "status_code": 200, "latency_ms": 31},
    )


def _api_seed_customer(context) -> StepOutput:
    context.state.set("customer.id", "CUS-501")
    return StepOutput(
        data={"customer_id": "CUS-501"}, metadata={"platform": "api", "status_code": 201, "latency_ms": 38}
    )


def _web_build_cart(context) -> StepOutput:
    customer_id = context.state.require("customer.id")
    context.state.set("cart.id", "CART-777")
    artifact = _write_json_artifact(context, "web-cart.json", {"customer_id": customer_id, "cart_id": "CART-777"})
    return StepOutput(
        data={"cart_id": "CART-777", "items": 2},
        metadata={"platform": "web", "browser": "chromium", "component": "cart"},
        artifacts=(artifact,),
    )


def _api_authorize_payment(context) -> StepOutput:
    context.state.require("cart.id")
    context.state.set("payment.id", "PAY-900")
    return StepOutput(
        data={"payment_id": "PAY-900"}, metadata={"platform": "api", "status_code": 202, "latency_ms": 57}
    )


def _mobile_push_confirmation(context) -> StepOutput:
    attempts = int(context.state.get("mobile.push.attempts", 0)) + 1
    context.state.set("mobile.push.attempts", attempts)
    if attempts == 1:
        raise RuntimeError("Push confirmation was not visible yet")
    artifact = _write_json_artifact(context, "mobile-push.json", {"payment_id": context.state.require("payment.id")})
    return StepOutput(
        data={"push_visible": True, "attempts": attempts},
        metadata={"platform": "mobile", "device_name": "sample-simulator", "context": "native"},
        artifacts=(artifact,),
    )


def _write_json_artifact(context, name: str, payload: dict) -> ArtifactRef:
    path = context.artifact_path(name)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return ArtifactRef(name=Path(name).stem, artifact_type="json", path=path, mime_type="application/json")
