import json
from decimal import Decimal
from pathlib import Path

from google.cloud import bigquery

project_root = Path(__file__).resolve().parents[1]
policy_path = project_root / "policies" / "R001_HIGH_CLAIM_AMOUNT.json"
policy = json.loads(policy_path.read_text(encoding="utf-8"))

client = bigquery.Client(project="compliance-agent-509701")
sql = """
SELECT
  transaction_id, pharmacy_id, claim_amount, claim_status, rule_id,
  routine_claim_count, routine_avg_amount, amount_vs_pharmacy_average
FROM `compliance-agent-509701.compliance_analytics.v_case_evidence`
ORDER BY transaction_id
"""

cases = list(client.query(sql, location="US").result())

for row in cases:
    evidence = dict(row.items())

    if evidence["rule_id"] != policy["policy_id"]:
        raise ValueError(f"Unexpected rule for {evidence['transaction_id']}")

    missing = [
        field for field in policy["required_evidence"]
        if evidence.get(field) is None
    ]
    minimum_count = policy["review_criteria"]["minimum_routine_claims"]
    minimum_ratio = Decimal(
        str(policy["review_criteria"]["minimum_amount_ratio"])
    )

    if missing or evidence["routine_claim_count"] < minimum_count:
        recommendation = "NEEDS_MORE_EVIDENCE"
    elif Decimal(str(evidence["amount_vs_pharmacy_average"])) >= minimum_ratio:
        recommendation = "INVESTIGATOR_REVIEW"
    else:
        recommendation = "MONITOR"

    print(json.dumps({
        "transaction_id": evidence["transaction_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "recommendation": recommendation,
        "amount_vs_pharmacy_average": evidence["amount_vs_pharmacy_average"],
        "missing_evidence": missing
    }, default=str))