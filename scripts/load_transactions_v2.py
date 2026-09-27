from pathlib import Path
from google.cloud import bigquery

project_id = "compliance-agent-509701"
table_id = f"{project_id}.compliance_analytics.pharmacy_transactions_v2"
csv_path = (
    Path(__file__).resolve().parents[1]
    / "data" / "generated" / "pharmacy_transactions_v2.csv"
)

schema = [
    bigquery.SchemaField("transaction_id", "STRING"),
    bigquery.SchemaField("transaction_date", "DATE"),
    bigquery.SchemaField("pharmacy_id", "STRING"),
    bigquery.SchemaField("patient_id", "STRING"),
    bigquery.SchemaField("prescriber_id", "STRING"),
    bigquery.SchemaField("drug_id", "STRING"),
    bigquery.SchemaField("quantity", "INTEGER"),
    bigquery.SchemaField("claim_amount", "NUMERIC"),
    bigquery.SchemaField("claim_status", "STRING"),
    bigquery.SchemaField("source_system", "STRING"),
]

client = bigquery.Client(project=project_id)
config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

with csv_path.open("rb") as csv_file:
    job = client.load_table_from_file(
        csv_file, table_id, job_config=config, location="US"
    )

job.result()
table = client.get_table(table_id)
print(f"Loaded {table.num_rows} rows into {table_id}")