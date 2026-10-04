import argparse
import json
from pathlib import Path

from google.cloud import bigquery

from evaluate_r002 import evaluate_repeat_pair
from policy_engine import evaluate_case


PROJECT = "compliance-agent-509701"
ROOT = Path(__file__).resolve().parents[1]


def load_policy(filename):
    path = ROOT / "policies" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def get_evidence(case_id):
    client = bigquery.Client(project=PROJECT)

    sql = """
    SELECT
      c.*,
      p.transaction_id AS prior_record_id,
      p.transaction_date AS prior_record_date,
      p.patient_id AS prior_patient_id,
      p.pharmacy_id AS prior_pharmacy_id,
      p.drug_id AS prior_drug_id,
      p.quantity AS prior_quantity,
      p.claim_amount AS prior_claim_amount,
      p.claim_status AS prior_claim_status,
      p.quality_status AS prior_quality_status
    FROM `compliance-agent-509701.compliance_analytics.v2_case_evidence` AS c
    LEFT JOIN `compliance-agent-509701.compliance_analytics.v2_claim_quality` AS p
      ON c.prior_transaction_id = p.transaction_id
    WHERE c.case_id = @case_id
    LIMIT 2
    """

    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("case_id", "STRING", case_id)
        ]
    )
    rows = list(client.query(sql, job_config=config, location="US").result())

    if len(rows) != 1:
        raise LookupError(f"Expected one case for {case_id}; found {len(rows)}")

    # Convert BigQuery DATE and NUMERIC values to JSON-compatible strings.
    return json.loads(json.dumps(dict(rows[0].items()), default=str))


def build_report(evidence):
    decisions = []

    if "R001_HIGH_CLAIM_AMOUNT" in evidence["rule_ids"]:
        policy = load_policy("R001_HIGH_CLAIM_AMOUNT.json")

        if evidence["quality_status"] != policy["flag_criteria"]["quality_status"]:
            raise ValueError("R001 case did not pass the required quality check")

        r001_evidence = {**evidence, "rule_id": policy["policy_id"]}
        recommendation, missing = evaluate_case(r001_evidence, policy)

        decisions.append({
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"],
            "decision": recommendation,
            "missing_evidence": missing,
            "human_approval_required_for_escalation":
                policy["human_approval_required_for_escalation"],
        })

    if "R002_REPEAT_FILL" in evidence["rule_ids"]:
        policy = load_policy("R002_REPEAT_FILL.json")
        decisions.append(evaluate_repeat_pair(evidence, policy))

    if not decisions:
        raise ValueError("Case contains no supported rule IDs")

    return {
        "case_id": evidence["case_id"],
        "evidence": evidence,
        "policy_decisions": decisions,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    args = parser.parse_args()

    evidence = get_evidence(args.case_id)
    report = build_report(evidence)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()