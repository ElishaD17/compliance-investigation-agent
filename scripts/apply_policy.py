import json
from decimal import Decimal
from pathlib import Path

from google.cloud import bigquery
from policy_engine import evaluate_case

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

    recommendation, missing = evaluate_case(evidence, policy)

    print(json.dumps({
        "transaction_id": evidence["transaction_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "recommendation": recommendation,
        "amount_vs_pharmacy_average": evidence["amount_vs_pharmacy_average"],
        "missing_evidence": missing
    }, default=str))