import tempfile
import unittest
from pathlib import Path

from mercy_app.brain import Incident, LayeredBrain


class LayeredBrainTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "memory.sqlite3"
        self.incident = Incident(
            source="mock",
            error_type="TypeError",
            message="value 42 is not iterable",
            stack_trace="trace",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_first_run_requires_review_and_not_run_tests_block_progress(self):
        brain = LayeredBrain(self.database)
        first = brain.record_run(self.incident, "passed")
        blocked = brain.record_run(self.incident, "not_run")
        brain.close()

        self.assertEqual(first.action, "candidate_needs_review")
        self.assertEqual(first.confidence, 0.0)
        self.assertEqual(blocked.action, "tests_required")

    def test_human_feedback_changes_later_decisions(self):
        brain = LayeredBrain(self.database)
        for _ in range(3):
            prior = brain.record_run(self.incident, "passed")
            brain.record_feedback(prior.run_id, "accepted")

        next_decision = brain.record_run(self.incident, "passed")
        brain.close()

        self.assertEqual(next_decision.action, "candidate_supported")
        self.assertEqual(next_decision.evidence_count, 3)
        self.assertEqual(next_decision.acceptance_rate, 1.0)
        self.assertGreater(next_decision.confidence, 0)

    def test_failed_tests_always_block_even_with_positive_history(self):
        brain = LayeredBrain(self.database)
        for _ in range(3):
            prior = brain.record_run(self.incident, "passed")
            brain.record_feedback(prior.run_id, "accepted")

        decision = brain.record_run(self.incident, "failed")
        brain.close()

        self.assertEqual(decision.action, "blocked_test_failure")

    def test_memory_survives_reopening_database(self):
        brain = LayeredBrain(self.database)
        prior = brain.record_run(self.incident, "passed")
        brain.record_feedback(prior.run_id, "rejected")
        brain.close()

        brain = LayeredBrain(self.database)
        decision = brain.record_run(self.incident, "passed")
        brain.close()

        self.assertEqual(decision.evidence_count, 1)
        self.assertEqual(decision.acceptance_rate, 0.0)
        self.assertEqual(decision.action, "candidate_needs_review")

    def test_history_shows_feedback_without_exposing_stack_trace(self):
        brain = LayeredBrain(self.database)
        incident = Incident(
            source="mock",
            error_type="ValueError",
            message="invalid state",
            stack_trace="PRIVATE_STACK_TRACE",
        )
        decision = brain.record_run(incident, "passed")
        summaries = brain.recent_runs()
        brain.record_feedback(decision.run_id, "rejected")
        summaries_with_feedback = brain.recent_runs()
        brain.close()

        self.assertEqual(len(summaries), 1)
        self.assertIsNone(summaries[0].feedback)
        self.assertEqual(summaries[0].message, "invalid state")
        self.assertFalse(hasattr(summaries[0], "stack_trace"))
        self.assertEqual(summaries_with_feedback[0].feedback, "rejected")

    def test_history_limit_is_bounded(self):
        brain = LayeredBrain(self.database)

        for limit in (0, 101):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    brain.recent_runs(limit)
        brain.close()

    def test_export_memory_includes_runs_and_feedback(self):
        brain = LayeredBrain(self.database)
        decision = brain.record_run(self.incident, "passed")
        brain.record_feedback(decision.run_id, "accepted", "onay")

        exported = brain.export_memory()
        brain.close()

        self.assertEqual(exported["version"], 1)
        self.assertEqual(len(exported["runs"]), 1)
        self.assertEqual(exported["runs"][0]["message"], self.incident.message)
        self.assertEqual(exported["runs"][0]["feedback"]["outcome"], "accepted")
        self.assertEqual(exported["runs"][0]["feedback"]["note"], "onay")

    def test_clear_memory_removes_all_runs_and_feedback(self):
        brain = LayeredBrain(self.database)
        decision = brain.record_run(self.incident, "passed")
        brain.record_feedback(decision.run_id, "rejected")

        brain.clear_memory()
        self.assertEqual(brain.recent_runs(), [])
        self.assertEqual(brain.export_memory()["runs"], [])
        brain.close()


if __name__ == "__main__":
    unittest.main()
