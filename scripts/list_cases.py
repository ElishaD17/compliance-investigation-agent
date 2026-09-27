from google.cloud import bigquery

client = bigquery.Client(project="compliance-agent-509701")

sql = """
SELECT
  transaction_id,
  pharmacy_id,
  claim_amount,
  routine_claim_count,
  routine_avg_amount,
  amount_vs_pharmacy_average,
  rule_id
FROM `compliance-agent-509701.compliance_analytics.v_case_evidence`
ORDER BY transaction_id
"""

cases = list(client.query(sql, location="US").result())
print(f"Cases for review: {len(cases)}")

for case in cases:
    print(
        f"{case.transaction_id} | {case.pharmacy_id} | "
        f"${case.claim_amount} | pharmacy average ${case.routine_avg_amount} | "
        f"{case.amount_vs_pharmacy_average}x average | {case.rule_id}"
    )