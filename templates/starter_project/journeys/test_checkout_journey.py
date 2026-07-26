from __future__ import annotations

from full_stack_automation_orchestrator import Journey, JourneyRunner, JourneyStep, StepOutput


def create_order(context):
    order_id = "ORD-1001"
    context.state.set("order.id", order_id)
    return StepOutput(data={"order_id": order_id}, metadata={"platform": "api"})


def verify_web_order(context):
    order_id = context.state.require("order.id")
    return StepOutput(data={"visible_order": order_id}, metadata={"platform": "web"})


def verify_mobile_order(context):
    order_id = context.state.require("order.id")
    return StepOutput(data={"visible_order": order_id}, metadata={"platform": "mobile"})


def test_checkout_journey():
    journey = Journey(
        name="Checkout works across API, Web, and Mobile",
        suite="checkout",
        domain="orders",
        steps=[
            JourneyStep("Create order through API", create_order, platform="api"),
            JourneyStep(
                "Verify order in Web", verify_web_order, platform="web", depends_on=("Create order through API",)
            ),
            JourneyStep(
                "Verify order in Mobile",
                verify_mobile_order,
                platform="mobile",
                depends_on=("Create order through API",),
            ),
        ],
    )

    result = JourneyRunner().run(journey)

    assert result.passed
