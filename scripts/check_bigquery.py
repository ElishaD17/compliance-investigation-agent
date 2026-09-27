from google.cloud import bigquery

PROJECT_ID = "compliance-agent-509701"

client = bigquery.Client(project=PROJECT_ID)

sql = """
SELECT COUNT(*) AS transaction_count
FROM `compliance-agent-509701.compliance_analytics.pharmacy_transactions`
"""

rows = client.query(sql, location="US").result()
for row in rows:
    print(f"BigQuery connection successful: {row.transaction_count} transactions")