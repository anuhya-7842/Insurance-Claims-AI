
from src.claims_engine import assess_claim


def make_test_data():
    claim = {
        "claim_id": "CLM-2026-000001",
        "claim_type": "AUTO",
        "claimed_amount": 5000.0,
    }

    policy = {
        "policy_id": "POL-AUTO-2026-000001",
        "product_type": "AUTO",
        "status": "ACTIVE",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    }

    coverage = {
        "coverage_id": "COV-000001",
        "limit_amount": 10000.0,
        "deductible_amount": 500.0,
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
    }

    incident = {
        "incident_id": "INC-000001",
        "incident_date": "2026-06-15",
    }

    documents = [
        {
            "document_type": "CLAIM_FORM",
            "status": "RECEIVED",
            "received_at": "2026-06-16T10:00:00",
        },
        {
            "document_type": "INCIDENT_REPORT",
            "status": "RECEIVED",
            "received_at": "2026-06-16T10:00:00",
        },
        {
            "document_type": "INVOICE",
            "status": "RECEIVED",
            "received_at": "2026-06-16T10:00:00",
        },
    ]

    return claim, policy, coverage, incident, documents


def test_eligible_claim():
    claim, policy, coverage, incident, documents = make_test_data()

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "ELIGIBLE"
    assert result["recommended_amount"] == 4500.0
    assert result["preliminary_reserve"] == 4500.0
    assert result["decision_reason"] == (
        "COVERAGE_AND_DOCUMENT_CHECKS_PASSED"
    )


def test_incident_before_policy_start():
    claim, policy, coverage, incident, documents = make_test_data()
    incident["incident_date"] = "2025-12-31"

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "INELIGIBLE"
    assert result["recommended_amount"] == 0.0
    assert "INCIDENT_BEFORE_POLICY_START" in result["decision_reason"]


def test_cancelled_policy():
    claim, policy, coverage, incident, documents = make_test_data()
    policy["status"] = "CANCELLED"

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "INELIGIBLE"
    assert "POLICY_CANCELLED" in result["decision_reason"]


def test_missing_mandatory_document():
    claim, policy, coverage, incident, documents = make_test_data()
    documents = [
        doc for doc in documents
        if doc["document_type"] != "INVOICE"
    ]

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "NEEDS_DOCUMENTS"
    assert "MISSING_DOCUMENTS:INVOICE" in result["decision_reason"]


def test_claim_exceeding_coverage_limit():
    claim, policy, coverage, incident, documents = make_test_data()
    claim["claimed_amount"] = 15000.0

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "NEEDS_REVIEW"
    assert result["recommended_amount"] == 10000.0
    assert "CLAIM_AMOUNT_EXCEEDS_LIMIT" in result["decision_reason"]


def test_claim_type_mismatch():
    claim, policy, coverage, incident, documents = make_test_data()
    claim["claim_type"] = "HEALTH"

    result = assess_claim(
        claim, policy, coverage, incident, documents
    )

    assert result["eligibility"] == "INELIGIBLE"
    assert "CLAIM_TYPE_MISMATCH" in result["decision_reason"]
def test_duplicate_claim_needs_review():
    claim, policy, coverage, incident, documents = make_test_data()
    claim["policy_id"] = policy["policy_id"]
    claim["incident_id"] = incident["incident_id"]

    all_claims = [
        claim,
        {
            "claim_id": "CLM-2026-000002",
            "policy_id": claim.get("policy_id", policy["policy_id"]),
            "incident_id": incident["incident_id"],
        },
    ]

    result = assess_claim(
        claim,
        policy,
        coverage,
        incident,
        documents,
        all_claims=all_claims,
    )

    assert result["eligibility"] == "NEEDS_REVIEW"
    assert "DUPLICATE_CLAIM" in result["decision_reason"]
    
def test_duplicate_payment_needs_review():
    claim, policy, coverage, incident, documents = make_test_data()

    all_settlements = [
        {
            "settlement_id": "SET-001",
            "claim_id": claim["claim_id"],
            "amount": 500,
            "status": "PAID",
        },
        {
            "settlement_id": "SET-002",
            "claim_id": claim["claim_id"],
            "amount": 500,
            "status": "PAID",
        },
    ]

    result = assess_claim(
        claim,
        policy,
        coverage,
        incident,
        documents,
        all_settlements=all_settlements,
    )

    assert result["eligibility"] == "NEEDS_REVIEW"
    assert "DUPLICATE_PAYMENT" in result["decision_reason"]
    
def test_settlement_exceeding_coverage_limit():
    claim, policy, coverage, incident, documents = make_test_data()

    all_settlements = [
        {
            "settlement_id": "SET-001",
            "claim_id": claim["claim_id"],
            "amount": float(coverage["limit_amount"]) + 100,
            "status": "PAID",
        },
    ]

    result = assess_claim(
        claim,
        policy,
        coverage,
        incident,
        documents,
        all_settlements=all_settlements,
    )

    assert result["eligibility"] == "NEEDS_REVIEW"
    assert (
        "SETTLEMENT_EXCEEDS_COVERAGE_LIMIT"
        in result["decision_reason"]
    )


