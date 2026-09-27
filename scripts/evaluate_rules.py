import csv
import argparse
from pathlib import Path


from google.cloud import bigquery

parser = argparse.ArgumentParser()
parser.add_argument("--source", choices=["r001", "combined"], required=True)
args = parser.parse_args()

views = {
    "r001": "v2_high_amount_flags",
    "combined": "v2_case_candidates",
}
view_name = views[args.source]


root = Path(__file__).resolve().parents[1]
truth_path = root / "data" / "generated" / "ground_truth_v2.csv"

with truth_path.open(newline="", encoding="utf-8") as file:
    truth_rows = list(csv.DictReader(file))

truth = {
    row["transaction_id"]: row["expected_review"] == "1"
    for row in truth_rows
}
if len(truth) != 50_000:
    raise ValueError("Expected 50,000 unique ground-truth transaction IDs")

client = bigquery.Client(project="compliance-agent-509701")
sql = f"""
SELECT transaction_id
FROM `compliance-agent-509701.compliance_analytics.{view_name}`
"""
flag_rows = list(client.query(sql, location="US").result())
flagged = {row.transaction_id for row in flag_rows}

if len(flagged) != len(flag_rows):
    raise ValueError("Duplicate transaction IDs in the flag view")
if not flagged.issubset(truth):
    raise ValueError("BigQuery contains IDs missing from local ground truth")

positive = {transaction_id for transaction_id, label in truth.items() if label}

tp = len(flagged & positive)
fp = len(flagged - positive)
fn = len(positive - flagged)
tn = len(truth) - tp - fp - fn

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0

print(f"True positives:  {tp}")
print(f"False positives: {fp}")
print(f"False negatives: {fn}")
print(f"True negatives:  {tn}")
print(f"Precision:       {precision:.1%}")
print(f"Recall:          {recall:.1%}")