import argparse
import json
import os

from google import genai
from pydantic import BaseModel, Field

from build_case_report import build_report, get_evidence


class DraftSummary(BaseModel):
    narrative: str = Field(
        description="Two or three factual sentences explaining the case"
    )
    evidence_fields: list[str] = Field(
        description="Exact field names from the supplied evidence used in the narrative"
    )
    investigator_question: str = Field(
        description="One question a human investigator should resolve"
    )


def draft_report(report):
    evidence = report["evidence"]

    fields = [
        "transaction_id",
        "transaction_date",
        "claim_amount",
        "claim_status",
        "quality_status",
    ]

    if "R001_HIGH_CLAIM_AMOUNT" in evidence["rule_ids"]:
        fields += [
            "pharmacy_id",
            "routine_claim_count",
            "routine_avg_amount",
            "amount_vs_pharmacy_average",
        ]

    if "R002_REPEAT_FILL" in evidence["rule_ids"]:
        fields += [
            "patient_id",
            "pharmacy_id",
            "drug_id",
            "quantity",
            "prior_record_id",
            "prior_record_date",
            "prior_patient_id",
            "prior_pharmacy_id",
            "prior_drug_id",
            "prior_quantity",
            "prior_claim_amount",
            "prior_claim_status",
            "prior_quality_status",
        ]

    facts = {field: evidence[field] for field in fields}

    prompt = f"""
Write a short investigator-facing case summary using ONLY the supplied facts.
The policy decisions below were calculated by deterministic Python code.
Do not change them or claim that fraud or an improper fill has been proven.
Describe the evidence and one question for a human investigator.
Use exact evidence field names in evidence_fields.

Verified evidence:
{json.dumps(facts, indent=2, default=str)}

Policy decisions:
{json.dumps(report["policy_decisions"], indent=2, default=str)}
"""

    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is not set in this PowerShell session")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    interaction = client.interactions.create(
        model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": DraftSummary.model_json_schema(),
        },
    )

    draft = DraftSummary.model_validate_json(interaction.output_text)

    if not draft.evidence_fields or not set(draft.evidence_fields).issubset(facts):
        raise ValueError("Summary cited an unknown evidence field")

    return {
        "case_id": report["case_id"],
        "policy_decisions": report["policy_decisions"],
        "verified_facts": facts,
        "draft_summary": draft.model_dump(),
        "status": "DRAFT_FOR_HUMAN_REVIEW",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    args = parser.parse_args()

    report = build_report(get_evidence(args.case_id))
    result = draft_report(report)
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()