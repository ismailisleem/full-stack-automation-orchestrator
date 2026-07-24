from __future__ import annotations

import pytest

from full_stack_automation_orchestrator.state import MissingStateError, ScenarioState


def test_state_stores_json_safe_values():
    state = ScenarioState()
    state.set("order.id", "ORD-1")
    state.append("events", {"name": "created"})

    assert state.require("order.id") == "ORD-1"
    assert state.snapshot()["events"] == [{"name": "created"}]


def test_state_requires_existing_value():
    state = ScenarioState()

    with pytest.raises(MissingStateError):
        state.require("missing")


def test_state_namespace_returns_prefixed_values():
    state = ScenarioState({"api.token": "abc", "api.user": "u1", "web.browser": "chromium"})

    assert state.namespace("api") == {"token": "abc", "user": "u1"}
