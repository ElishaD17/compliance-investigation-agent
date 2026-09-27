from decimal import Decimal


def evaluate_case(evidence, policy):
    if evidence.get("rule_id") != policy["policy_id"]:
        raise ValueError("Case rule does not match the selected policy")

    if (
        evidence.get("claim_status") != policy["flag_criteria"]["claim_status"]
        or Decimal(str(evidence["claim_amount"]))
        < Decimal(str(policy["flag_criteria"]["minimum_claim_amount"]))
    ):
        raise ValueError("Case does not meet the flag criteria")

    missing = [
        field for field in policy["required_evidence"]
        if evidence.get(field) is None
    ]

    minimum_count = policy["review_criteria"]["minimum_routine_claims"]
    minimum_ratio = Decimal(
        str(policy["review_criteria"]["minimum_amount_ratio"])
    )

    if missing or evidence["routine_claim_count"] < minimum_count:
        return "NEEDS_MORE_EVIDENCE", missing
    if Decimal(str(evidence["amount_vs_pharmacy_average"])) >= minimum_ratio:
        return "INVESTIGATOR_REVIEW", missing
    return "MONITOR", missing