import csv
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from policy_engine import evaluate_case


class PolicyTests(unittest.TestCase):
    def test_review_scenarios(self):
        policy = json.loads(
            (ROOT / "policies" / "R001_HIGH_CLAIM_AMOUNT.json")
            .read_text(encoding="utf-8")
        )

        with (ROOT / "tests" / "fixtures" / "policy_cases.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            scenarios = list(csv.DictReader(file))

        self.assertEqual(len(scenarios), 5)

        for case in scenarios:
            with self.subTest(scenario=case["scenario_id"]):
                evidence = {
                    "transaction_id": "TEST-" + case["scenario_id"],
                    "pharmacy_id": "PHARM-TEST",
                    "rule_id": policy["policy_id"],
                    "claim_status": case["claim_status"],
                    "claim_amount": Decimal(case["claim_amount"]),
                    "routine_claim_count": (
                        int(case["routine_claim_count"])
                        if case["routine_claim_count"] else None
                    ),
                    "routine_avg_amount": (
                        Decimal(case["routine_avg_amount"])
                        if case["routine_avg_amount"] else None
                    ),
                    "amount_vs_pharmacy_average": (
                        Decimal(case["amount_vs_pharmacy_average"])
                        if case["amount_vs_pharmacy_average"] else None
                    ),
                }
                actual, _ = evaluate_case(evidence, policy)
                self.assertEqual(actual, case["expected_recommendation"])


if __name__ == "__main__":
    unittest.main()