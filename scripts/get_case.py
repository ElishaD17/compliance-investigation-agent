import argparse
import json

from google.cloud import bigquery

parser = argparse.ArgumentParser()
parser.add_argument("--case-id", required=True)
args = parser.parse_args()

client = bigquery.Client(project="compliance-agent-509701")

sql = """
SELECT *
FROM `compliance-agent-509701.compliance_analytics.v2_case_evidence`
WHERE case_id = @case_id
LIMIT 2
"""

config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("case_id", "STRING", args.case_id)
    ]
)

rows = list(client.query(sql, job_config=config, location="US").result())

if len(rows) != 1:
    raise LookupError(f"Expected one case for {args.case_id}; found {len(rows)}")

print(json.dumps(dict(rows[0].items()), indent=2, default=str))