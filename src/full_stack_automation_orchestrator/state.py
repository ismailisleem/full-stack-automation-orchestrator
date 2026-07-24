from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from full_stack_automation_orchestrator.models import json_safe


class MissingStateError(KeyError):
    """Raised when a required scenario state value is absent."""


class ScenarioState:
    """Small JSON-safe state bag shared across API, Web, and Mobile phases."""

    def __init__(self, initial: Mapping[str, Any] | None = None) -> None:
        self._values: dict[str, Any] = dict(initial or {})

    def set(self, key: str, value: Any) -> Any:
        self._values[key] = json_safe(value)
        return value

    def update(self, values: Mapping[str, Any]) -> None:
        for key, value in values.items():
            self.set(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def require(self, key: str) -> Any:
        if key not in self._values:
            raise MissingStateError(f"Missing scenario state value: {key}")
        return self._values[key]

    def append(self, key: str, value: Any) -> list[Any]:
        existing = self._values.setdefault(key, [])
        if not isinstance(existing, list):
            raise TypeError(f"State key '{key}' is not a list")
        existing.append(json_safe(value))
        return existing

    def namespace(self, prefix: str) -> dict[str, Any]:
        dotted = prefix.rstrip(".") + "."
        return {
            key.removeprefix(dotted): deepcopy(value) for key, value in self._values.items() if key.startswith(dotted)
        }

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self._values)

    def __contains__(self, key: object) -> bool:
        return key in self._values
