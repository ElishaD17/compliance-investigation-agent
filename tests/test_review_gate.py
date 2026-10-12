import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from review_case_graph import human_review


class ReviewGateTests(unittest.TestCase):
    def test_monitor_case_cannot_be_approved_for_escalation(self):
        state = {
            "case_id": "TEST-MONITOR",
            "result": {
                "policy_decisions": [{
                    "decision": "MONITOR",
                    "human_approval_required_for_escalation": True,
                }]
            },
        }
        response = {
            "decision": "APPROVE_ESCALATION",
            "reviewer": "Test Reviewer",
            "note": "Attempted approval",
        }

        with patch("review_case_graph.interrupt", return_value=response):
            with self.assertRaisesRegex(
                ValueError, "Policy does not permit this escalation"
            ):
                human_review(state)


if __name__ == "__main__":
    unittest.main()