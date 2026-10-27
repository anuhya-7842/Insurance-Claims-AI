
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
    ]

    for df, key, table in primary_keys:
        check_unique(df, key, table)

    # Foreign-key integrity.
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

    print("DATA VALIDATION PASSED")
    print(f"Customers: {len(customers)}")
    print(f"Policies: {len(policies)}")
    print(f"Claims: {len(claims)}")
    print(f"Incidents: {len(incidents)}")
    print(f"Documents: {len(documents)}")
    print(f"Claim types: {claims['claim_type'].nunique()}")


if __name__ == "__main__":
    validate_data()
