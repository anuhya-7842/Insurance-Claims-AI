
from datetime import date


RULES_VERSION = "1.0"

REQUIRED_DOCUMENTS = {
    "CLAIM_FORM",
    "INCIDENT_REPORT",
    "INVOICE",
}


def assess_claim(
    claim,
    policy,
    coverage,
    incident,
    documents,
    all_claims=None,
    all_settlements=None,
):
    """
    Assess a claim using explicit business rules.

    Returns a deterministic decision with a reason,
    preliminary reserve, and recommended settlement.
    """

    reasons = []
    decision = "ELIGIBLE"
    # Rule 0: Detect duplicate claims and duplicate incidents.
    if all_claims is not None:
        for other_claim in all_claims:
            if other_claim["claim_id"] == claim["claim_id"]:
                continue

            if other_claim["incident_id"] == claim["incident_id"]:
                if other_claim["policy_id"] == claim["policy_id"]:
                    reasons.append("DUPLICATE_CLAIM")
                else:
                    reasons.append("DUPLICATE_INCIDENT")

                decision = "NEEDS_REVIEW"
                break
    # Rule: Flag multiple paid settlements for the same claim.
    if all_settlements is not None:
        paid_settlements = [
            settlement
            for settlement in all_settlements
            if settlement["claim_id"] == claim["claim_id"]
            and settlement["status"] == "PAID"
        ]

        if len(paid_settlements) > 1:
            if decision == "ELIGIBLE":
                decision = "NEEDS_REVIEW"
            reasons.append("DUPLICATE_PAYMENT")

    claimed_amount = float(claim["claimed_amount"])
    
    # Rule: Flag settlements that exceed the coverage limit.
    if all_settlements is not None:
        paid_total = sum(
            float(settlement["amount"])
            for settlement in all_settlements
            if settlement["claim_id"] == claim["claim_id"]
            and settlement["status"] == "PAID"
        )

        if paid_total > float(coverage["limit_amount"]):
            if decision == "ELIGIBLE":
                decision = "NEEDS_REVIEW"
            reasons.append("SETTLEMENT_EXCEEDS_COVERAGE_LIMIT")

    limit_amount = float(coverage["limit_amount"])
    deductible = float(coverage["deductible_amount"])

    incident_date = date.fromisoformat(incident["incident_date"])
    policy_start = date.fromisoformat(policy["start_date"])
    policy_end = date.fromisoformat(policy["end_date"])
    coverage_start = date.fromisoformat(coverage["effective_from"])
    coverage_end = date.fromisoformat(coverage["effective_to"])

    # Rule 1: Incident must occur during policy coverage.
    if incident_date < policy_start:
        decision = "INELIGIBLE"
        reasons.append("INCIDENT_BEFORE_POLICY_START")

    elif incident_date > policy_end:
        decision = "INELIGIBLE"
        reasons.append("INCIDENT_AFTER_POLICY_END")

    elif incident_date < coverage_start or incident_date > coverage_end:
        decision = "INELIGIBLE"
        reasons.append("INCIDENT_OUTSIDE_COVERAGE_PERIOD")

    # Rule 2: Policy must not have been cancelled before the incident.
    cancellation_date = policy.get("cancellation_date")

    if (
        policy["status"] == "CANCELLED"
        and cancellation_date is not None
        and incident_date >= date.fromisoformat(cancellation_date)
    ):
        decision = "INELIGIBLE"
        reasons.append("POLICY_CANCELLED")

    # Rule 3: Claim type must match the policy product.
    if claim["claim_type"] != policy["product_type"]:
        decision = "INELIGIBLE"
        reasons.append("CLAIM_TYPE_MISMATCH")

    # Rule 4: Check required documents.
    received_types = {
        doc["document_type"]
        for doc in documents
        if doc["status"] == "RECEIVED"
        and doc.get("received_at")
    }

    missing_documents = sorted(REQUIRED_DOCUMENTS - received_types)

    if missing_documents and decision != "INELIGIBLE":
        decision = "NEEDS_DOCUMENTS"
        reasons.append(
            "MISSING_DOCUMENTS:" + ",".join(missing_documents)
        )

    # Rule 5: Claim amount exceeding coverage requires review.
    if claimed_amount > limit_amount:
        if decision == "ELIGIBLE":
            decision = "NEEDS_REVIEW"
        reasons.append("CLAIM_AMOUNT_EXCEEDS_LIMIT")

    # Rule 6: Calculate the recommendation from source values.
    # Deduct the deductible and cap the recommendation at the limit.
    recommended_amount = round(
        min(max(claimed_amount - deductible, 0), limit_amount),
        2,
    )

    # Ineligible claims must not receive a settlement recommendation.
    if decision == "INELIGIBLE":
        recommended_amount = 0.0

    if not reasons:
        reasons.append("COVERAGE_AND_DOCUMENT_CHECKS_PASSED")

    # Reserve is provisional, not an approved or paid settlement.
    preliminary_reserve = recommended_amount

    return {
        "claim_id": claim["claim_id"],
        "eligibility": decision,
        "recommended_amount": recommended_amount,
        "preliminary_reserve": preliminary_reserve,
        "decision_reason": ";".join(reasons),
        "rules_version": RULES_VERSION,
    }
