import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_r002 import evaluate_repeat_pair


class RepeatFillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "policies" / "R002_REPEAT_FILL.json"
        cls.policy = json.loads(path.read_text(encoding="utf-8"))

    def setUp(self):
        self.evidence = {
            "case_id": "TEST-CURRENT",
            "rule_ids": ["R002_REPEAT_FILL"],
            "transaction_id": "TEST-CURRENT",
            "transaction_date": "2026-06-22",
            "patient_id": "PAT-TEST",
            "pharmacy_id": "PHARM-TEST",
            "drug_id": "DRUG-TEST",
            "quantity": 35,
            "claim_amount": "197.99",
            "claim_status": "PAID",
            "quality_status": "PASS",
            "prior_transaction_id": "TEST-PRIOR",
            "prior_record_id": "TEST-PRIOR",
            "prior_record_date": "2026-06-15",
            "prior_patient_id": "PAT-TEST",
            "prior_pharmacy_id": "PHARM-TEST",
            "prior_drug_id": "DRUG-TEST",
            "prior_quantity": 35,
            "prior_claim_amount": "197.99",
            "prior_claim_status": "PAID",
            "prior_quality_status": "PASS",
        }

    def decision(self):
        return evaluate_repeat_pair(self.evidence, self.policy)["decision"]

    def test_exact_seven_day_boundary_is_review(self):
        self.assertEqual(self.decision(), "INVESTIGATOR_REVIEW")

    def test_same_day_pair_is_review(self):
        self.evidence["prior_record_date"] = "2026-06-22"
        self.assertEqual(self.decision(), "INVESTIGATOR_REVIEW")

    def test_eight_days_is_monitor(self):
        self.evidence["prior_record_date"] = "2026-06-14"
        self.assertEqual(self.decision(), "MONITOR")

    def test_different_quantity_is_monitor(self):
        self.evidence["prior_quantity"] = 36
        self.assertEqual(self.decision(), "MONITOR")

    def test_prior_claim_not_paid_is_monitor(self):
        self.evidence["prior_claim_status"] = "REJECTED"
        self.assertEqual(self.decision(), "MONITOR")

    def test_missing_prior_record_needs_evidence(self):
        self.evidence["prior_record_id"] = None
        self.assertEqual(self.decision(), "NEEDS_MORE_EVIDENCE")


if __name__ == "__main__":
    unittest.main()