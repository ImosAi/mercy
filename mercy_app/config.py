from pathlib import Path
from typing import Any

import yaml

from mercy_app.inputs import normalize_incident


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Yapılandırma kökü bir YAML nesnesi olmalı.")

    input_config = config.get("input")
    if not isinstance(input_config, dict):
        raise ValueError("'input' yapılandırması zorunludur ve nesne olmalıdır.")
    if input_config.get("source") != "mock":
        raise ValueError("Şu anda yalnızca input.source: mock destekleniyor.")
    if "incident" in input_config:
        incident = input_config["incident"]
        if not isinstance(incident, dict):
            raise ValueError("'input.incident' bir YAML nesnesi olmalıdır.")
        normalize_incident(incident, source="mock")

    memory_config = config.get("memory")
    if not isinstance(memory_config, dict) or not isinstance(
        memory_config.get("database"), str
    ):
        raise ValueError("'memory.database' bir SQLite dosya yolu olmalıdır.")

    simulation_config = config.get("simulation", {})
    if not isinstance(simulation_config, dict):
        raise ValueError("'simulation' yapılandırması nesne olmalıdır.")
    if simulation_config.get("test_status", "not_run") not in {
        "passed",
        "failed",
        "not_run",
    }:
        raise ValueError(
            "'simulation.test_status' passed, failed veya not_run olmalıdır."
        )

    return config
