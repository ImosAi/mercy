from collections.abc import Mapping
from typing import Protocol

from mercy_app.brain import Incident


class InputAdapter(Protocol):
    def fetch(self) -> Incident:
        """Fetch one incident and return it in Mercy's normalized event format."""


def normalize_incident(payload: Mapping[str, object], source: str) -> Incident:
    error_type = payload.get("error_type")
    message = payload.get("message")
    stack_trace = payload.get("stack_trace", "")

    if not isinstance(error_type, str) or not error_type.strip():
        raise ValueError("Olay 'error_type' alanı boş olmayan bir metin olmalıdır.")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Olay 'message' alanı boş olmayan bir metin olmalıdır.")
    if not isinstance(stack_trace, str):
        raise ValueError("Olay 'stack_trace' alanı metin olmalıdır.")
    if not source.strip():
        raise ValueError("Olay kaynağı boş olamaz.")

    return Incident(
        source=source.strip(),
        error_type=error_type.strip(),
        message=message.strip(),
        stack_trace=stack_trace.strip(),
    )


class MockInputAdapter:
    def __init__(self, incident: Mapping[str, object] | None = None):
        self._incident = incident if incident is not None else {
            "error_type": "TypeError",
            "message": "'NoneType' object is not iterable",
            "stack_trace": (
                'File "/app/service.py", line 42, in process_data\n'
                "    for item in data"
            ),
        }

    def fetch(self) -> Incident:
        return normalize_incident(self._incident, source="mock")


def create_input_adapter(config: Mapping[str, object]) -> InputAdapter:
    source = config.get("source")
    if source == "mock":
        incident = config.get("incident")
        if incident is not None and not isinstance(incident, Mapping):
            raise ValueError("'input.incident' bir YAML nesnesi olmalıdır.")
        return MockInputAdapter(incident)
    raise ValueError(f"Desteklenmeyen girdi kaynağı: {source!r}")
