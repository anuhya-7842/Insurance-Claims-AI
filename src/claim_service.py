
import pandas as pd

from src.claims_engine import assess_claim


DATA_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent / "data"


def load_table(name):
    path = DATA_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {name}.csv")

    return pd.read_csv(path).fillna("")


def get_record(df, column, value):
    matches = df[df[column] == value]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def process_claim(claim_id):
    claims = load_table("claims")
    policies = load_table("policies")
    coverages = load_table("coverages")
    incidents = load_table("incidents")
    documents = load_table("documents")
    settlements = load_table("settlements")

    claim = get_record(claims, "claim_id", claim_id)

    if claim is None:
        return {
            "error": "Claim not found",
            "claim_id": claim_id,
        }, 404

    policy = get_record(
        policies, "policy_id", claim["policy_id"]
    )

    incident = get_record(
        incidents, "incident_id", claim["incident_id"]
    )

    coverage = get_record(
        coverages, "policy_id", claim["policy_id"]
    )

    if policy is None or incident is None or coverage is None:
        return {
            "error": "Required claim relationships are missing",
            "claim_id": claim_id,
        }, 422

    claim_documents = documents[
        documents["claim_id"] == claim_id
    ].to_dict(orient="records")

    result = assess_claim(
        claim=claim,
        policy=policy,
        coverage=coverage,
        incident=incident,
        documents=claim_documents,
        all_claims=claims.to_dict(orient="records"),
        all_settlements=settlements.to_dict(orient="records"),
    )

    return result, 200
