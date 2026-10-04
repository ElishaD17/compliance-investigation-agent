import argparse
import json

from google.cloud import bigquery

parser = argparse.ArgumentParser()
parser.add_argument("--case-id", required=True)
args = parser.parse_args()

client = bigquery.Client(project="compliance-agent-509701")

sql = """
SELECT
  c.case_id,
  c.rule_ids,
  c.transaction_id,
  c.transaction_date,
  c.patient_id,
  c.pharmacy_id,
  c.drug_id,
  c.quantity,
  c.claim_amount,
  c.claim_status,
  c.quality_status,
  c.prior_transaction_id,
  p.transaction_id AS prior_record_id,
  p.transaction_date AS prior_record_date,
  p.patient_id AS prior_patient_id,
  p.pharmacy_id AS prior_pharmacy_id,
  p.drug_id AS prior_drug_id,
  p.quantity AS prior_quantity,
  p.claim_amount AS prior_claim_amount,
  p.claim_status AS prior_claim_status,
  p.quality_status AS prior_quality_status,
  DATE_DIFF(c.transaction_date, p.transaction_date, DAY) AS days_between
FROM `compliance-agent-509701.compliance_analytics.v2_case_evidence` AS c
LEFT JOIN `compliance-agent-509701.compliance_analytics.v2_claim_quality` AS p
  ON c.prior_transaction_id = p.transaction_id
WHERE c.case_id = @case_id
LIMIT 2
"""

config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("case_id", "STRING", args.case_id)
    ]
)
rows = list(client.query(sql, job_config=config, location="US").result())

if len(rows) != 1:
    raise LookupError(f"Expected one case; found {len(rows)}")
if "R002_REPEAT_FILL" not in rows[0].rule_ids:
    raise ValueError("This case was not flagged by R002")

print(json.dumps(dict(rows[0].items()), indent=2, default=str))