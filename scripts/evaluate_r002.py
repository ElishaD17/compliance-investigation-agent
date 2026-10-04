import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parents[1]
policy_path = root / "policies" / "R002_REPEAT_FILL.json"

with policy_path.open(encoding="utf-8") as file:
    policy = json.load(file)

evidence = json.load(sys.stdin)

prior_fields = {
    "transaction_id": "prior_record_id",
    "transaction_date": "prior_record_date",
    "patient_id": "prior_patient_id",
    "pharmacy_id": "prior_pharmacy_id",
    "drug_id": "prior_drug_id",
    "quantity": "prior_quantity",
    "claim_amount": "prior_claim_amount",
    "claim_status": "prior_claim_status",
    "quality_status": "prior_quality_status",
}

if "R002_REPEAT_FILL" not in evidence["rule_ids"]:
    raise ValueError("This case was not flagged by R002")

missing = [
    field
    for field in policy["required_prior_fields"]
    if evidence.get(prior_fields[field]) is None
]

if missing:
    decision = policy["decision_rules"]["missing_prior_record"]
    reason = f"Prior claim evidence is missing: {', '.join(missing)}"
else:
    matches = all(
        (
            Decimal(str(evidence[field]))
            == Decimal(str(evidence[prior_fields[field]]))
            if field == "claim_amount"
            else evidence[field] == evidence[prior_fields[field]]
        )
        for field in policy["match_fields"]
    )

    days_between = (
        date.fromisoformat(evidence["transaction_date"])
        - date.fromisoformat(evidence["prior_record_date"])
    ).days

    valid_pair = (
        evidence["prior_transaction_id"] == evidence["prior_record_id"]
        and matches
        and evidence["claim_status"] == "PAID"
        and evidence["prior_claim_status"] == "PAID"
        and evidence["quality_status"] == "PASS"
        and evidence["prior_quality_status"] == "PASS"
        and 0 <= days_between <= policy["maximum_days_between_claims"]
    )

    if valid_pair:
        decision = policy["decision_rules"]["verified_repeat_within_window"]
        reason = f"Matching paid claims occurred {days_between} day(s) apart"
    else:
        decision = policy["decision_rules"]["prior_record_conflicts_with_signal"]
        reason = "The retrieved pair does not satisfy all R002 policy checks"

print(json.dumps({
    "case_id": evidence["case_id"],
    "policy_id": policy["policy_id"],
    "decision": decision,
    "reason": reason,
    "human_approval_required_for_escalation":
        policy["human_approval_required_for_escalation"],
}, indent=2))