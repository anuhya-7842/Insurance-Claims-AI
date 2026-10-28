
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(name):
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return pd.read_csv(path)


def check_unique(df, column, table):
    if df[column].isna().any():
        raise ValueError(f"{table}.{column} contains null values")

    if df[column].duplicated().any():
        raise ValueError(f"{table}.{column} contains duplicate IDs")


def check_foreign_key(child, child_column, parent, parent_column, label):
    parent_ids = set(parent[parent_column].dropna())

    invalid = child[
        child[child_column].isna()
        | ~child[child_column].isin(parent_ids)
    ]

    if not invalid.empty:
        raise ValueError(
            f"{label}: {len(invalid)} invalid foreign-key rows"
        )


def validate_data():
    customers = load_csv("customers")
    policies = load_csv("policies")
    coverages = load_csv("coverages")
    incidents = load_csv("incidents")
    claims = load_csv("claims")
    items = load_csv("claim_items")
    documents = load_csv("documents")
    adjusters = load_csv("adjusters")
    assessments = load_csv("assessments")
    reserves = load_csv("reserves")
    claim_events = load_csv("claim_events")
    ground_truth = load_csv("ground_truth")

    # Primary-key uniqueness.
    primary_keys = [
        (customers, "customer_id", "customers"),
        (policies, "policy_id", "policies"),
        (coverages, "coverage_id", "coverages"),
        (incidents, "incident_id", "incidents"),
        (claims, "claim_id", "claims"),
        (items, "claim_item_id", "claim_items"),
        (documents, "document_id", "documents"),
        (adjusters, "adjuster_id", "adjusters"),
        (assessments, "assessment_id", "assessments"),
        (reserves, "reserve_id", "reserves"),
        (claim_events, "event_id", "claim_events"),
        (ground_truth, "claim_id", "ground_truth"),
    ]

    for df, key, table in primary_keys:
        check_unique(df, key, table)

    # Foreign-key integrity.
    check_foreign_key(
        incidents, "customer_id", customers, "customer_id",
        "Incident -> Customer"
    )
    check_foreign_key(
        policies, "customer_id", customers, "customer_id",
        "Policy -> Customer"
    )
    check_foreign_key(
        coverages, "policy_id", policies, "policy_id",
        "Coverage -> Policy"
    )
    check_foreign_key(
        claims, "policy_id", policies, "policy_id",
        "Claim -> Policy"
    )
    check_foreign_key(
        claims, "incident_id", incidents, "incident_id",
        "Claim -> Incident"
    )
    check_foreign_key(
        items, "claim_id", claims, "claim_id",
        "ClaimItem -> Claim"
    )
    check_foreign_key(
        documents, "claim_id", claims, "claim_id",
        "Document -> Claim"
    )
    check_foreign_key(
        assessments, "claim_id", claims, "claim_id",
        "Assessment -> Claim"
    )
    check_foreign_key(
        assessments, "adjuster_id", adjusters, "adjuster_id",
        "Assessment -> Adjuster"
    )
    check_foreign_key(
        reserves, "claim_id", claims, "claim_id",
        "Reserve -> Claim"
    )
    check_foreign_key(
        claim_events, "claim_id", claims, "claim_id",
        "ClaimEvent -> Claim"
    )
    check_foreign_key(
        ground_truth, "claim_id", claims, "claim_id",
        "GroundTruth -> Claim"
    )
        # Validate policy date ordering.
    policy_start = pd.to_datetime(
        policies["start_date"], errors="raise"
    )
    policy_end = pd.to_datetime(
        policies["end_date"], errors="raise"
    )

    assert policy_start.notna().all(), (
        "Policy start dates contain null values"
    )
    assert policy_end.notna().all(), (
        "Policy end dates contain null values"
    )
    assert (policy_start <= policy_end).all(), (
        "Policy start date must not be after end date"
    )
        # Validate incident dates.
    incident_dates = pd.to_datetime(
        incidents["incident_date"], errors="raise"
    )

    assert incident_dates.notna().all(), (
        "Incident dates contain null values"
    )
        # Validate document types and statuses.
    valid_document_types = {
        "CLAIM_FORM",
        "INCIDENT_REPORT",
        "INVOICE",
    }
    valid_document_statuses = {
        "RECEIVED",
        "PENDING",
        "REJECTED",
    }

    assert documents["document_type"].notna().all(), (
        "Document types contain null values"
    )
    assert documents["document_type"].isin(valid_document_types).all(), (
        "Invalid document type found"
    )
    assert documents["status"].notna().all(), (
        "Document statuses contain null values"
    )
    assert documents["status"].isin(valid_document_statuses).all(), (
        "Invalid document status found"
    )
        # Validate claim lifecycle status.
    valid_claim_statuses = {"SUBMITTED"}

    assert claims["status"].notna().all(), (
        "Claim statuses contain null values"
    )
    assert claims["status"].isin(valid_claim_statuses).all(), (
        "Invalid claim lifecycle status found"
    )
        # Validate assessment records.
    valid_eligibility_values = {
        "ELIGIBLE",
        "INELIGIBLE",
        "NEEDS_REVIEW",
        "NEEDS_DOCUMENTS",
    }

    assert assessments["eligibility"].notna().all(), (
        "Assessment eligibility contains null values"
    )
    assert assessments["eligibility"].isin(valid_eligibility_values).all(), (
        "Invalid assessment eligibility found"
    )
    assert assessments["decision_reason"].notna().all(), (
        "Assessment decision reasons contain null values"
    )
    assert assessments["decision_reason"].astype(str).str.strip().ne("").all(), (
        "Assessment decision reasons contain empty values"
    )
    assert assessments["rules_version"].notna().all(), (
        "Assessment rules versions contain null values"
    )
    assert assessments["rules_version"].astype(str).str.strip().ne("").all(), (
        "Assessment rules versions contain empty values"
    )

    # Required volume checks.
    assert len(policies) == 2000, "Expected 2,000 policies"
    assert len(claims) == 1000, "Expected 1,000 claims"
    assert claims["claim_type"].nunique() == 5, (
        "Expected five claim types"
    )

    # Allowed values.
    allowed_types = {
        "AUTO", "PROPERTY", "HEALTH", "TRAVEL", "LIABILITY"
    }
    assert set(claims["claim_type"]).issubset(allowed_types)

    # Non-negative monetary values.
    for table, df, column in [
        ("Policy", policies, "premium_amount"),
        ("Coverage", coverages, "limit_amount"),
        ("Coverage", coverages, "deductible_amount"),
        ("Claim", claims, "claimed_amount"),
        ("ClaimItem", items, "item_total"),
        ("Reserve", reserves, "amount"),
    ]:
        values = pd.to_numeric(df[column], errors="raise")
        assert values.notna().all(), f"{table}.{column} has nulls"
        assert (values >= 0).all(), (
            f"{table}.{column} contains negative values"
        )

    # Claim item arithmetic.
    expected_totals = (
        pd.to_numeric(items["amount"])
        * pd.to_numeric(items["quantity"])
    )
    actual_totals = pd.to_numeric(items["item_total"])

    assert (
        (expected_totals - actual_totals).abs() < 0.01
    ).all(), "Claim item totals do not reconcile"
    
    # Validate settlement records
    settlements = pd.read_csv(DATA_DIR / "settlements.csv").fillna("")

    assert settlements["settlement_id"].is_unique, (
        "Duplicate settlement IDs found"
    )

    assert settlements["claim_id"].isin(claims["claim_id"]).all(), (
        "Settlement references an unknown claim"
    )

    valid_settlement_statuses = {
        "PENDING", "APPROVED", "PAID", "REJECTED"
    }

    assert settlements["status"].isin(valid_settlement_statuses).all(), (
        "Invalid settlement status found"
    )

    assert (
        pd.to_numeric(settlements["amount"], errors="coerce").notna().all()
        and (pd.to_numeric(settlements["amount"], errors="coerce") >= 0).all()
    ), "Settlement amounts must be valid non-negative numbers"
        # Detect duplicate paid settlements without rejecting intentional test data.
    paid_settlements = settlements[
        settlements["status"] == "PAID"
    ]
    duplicate_paid_claims = int(
        paid_settlements["claim_id"].duplicated().sum()
    )

    print(
        "Claims with duplicate paid settlements: "
        f"{duplicate_paid_claims}"
    )


   
    summary = {
        "status": "PASSED",
        "counts": {
            "customers": len(customers),
            "policies": len(policies),
            "claims": len(claims),
            "incidents": len(incidents),
            "documents": len(documents),
            "claim_types": int(claims["claim_type"].nunique()),
        },
    }

    import json

    summary_path = DATA_DIR / "validation_summary.json"
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("DATA VALIDATION PASSED")
    print(f"Customers: {len(customers)}")
    print(f"Policies: {len(policies)}")
    print(f"Claims: {len(claims)}")
    print(f"Incidents: {len(incidents)}")
    print(f"Documents: {len(documents)}")
    print(f"Claim types: {claims['claim_type'].nunique()}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    validate_data()

