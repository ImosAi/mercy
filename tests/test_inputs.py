import tempfile
import unittest
from pathlib import Path

from mercy_app.config import load_config
from mercy_app.inputs import MockInputAdapter, create_input_adapter, normalize_incident


class InputAdapterTests(unittest.TestCase):
    def test_mock_adapter_returns_normalized_default_incident(self):
        incident = MockInputAdapter().fetch()

        self.assertEqual(incident.source, "mock")
        self.assertEqual(incident.error_type, "TypeError")
        self.assertEqual(incident.message, "'NoneType' object is not iterable")
        self.assertTrue(incident.stack_trace.startswith("File"))

    def test_normalizer_trims_fields_and_defaults_stack_trace(self):
        incident = normalize_incident(
            {"error_type": " ValueError ", "message": "  bad input  "},
            source=" mock ",
        )

        self.assertEqual(incident.source, "mock")
        self.assertEqual(incident.error_type, "ValueError")
        self.assertEqual(incident.message, "bad input")
        self.assertEqual(incident.stack_trace, "")

    def test_normalizer_rejects_missing_or_invalid_fields(self):
        invalid_payloads = (
            {},
            {"error_type": "TypeError", "message": " "},
            {
                "error_type": "TypeError",
                "message": "bad input",
                "stack_trace": [],
            },
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    normalize_incident(payload, source="mock")

    def test_factory_rejects_unsupported_sources(self):
        with self.assertRaisesRegex(ValueError, "Desteklenmeyen"):
            create_input_adapter({"source": "sentry"})

    def test_config_validates_optional_mock_incident(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mercy.yaml"
            config_path.write_text(
                """input:
  source: mock
  incident:
    error_type: ValueError
    message: Invalid customer state
memory:
  database: memory.sqlite3
""",
                encoding="utf-8",
            )

            config = load_config(config_path)
            incident = create_input_adapter(config["input"]).fetch()

        self.assertEqual(incident.error_type, "ValueError")
        self.assertEqual(incident.message, "Invalid customer state")

    def test_config_rejects_invalid_optional_mock_incident(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mercy.yaml"
            config_path.write_text(
                """input:
  source: mock
  incident:
    error_type: TypeError
memory:
  database: memory.sqlite3
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "message"):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
