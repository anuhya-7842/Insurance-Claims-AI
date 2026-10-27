import csv
from datetime import datetime
import pandas as pd

from src.claims_engine import assess_claim


DATA_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent / "data"

def log_claim_event(claim_id, event_type, details):
    events_path = DATA_DIR / "claim_events.csv"

    if not events_path.exists():
        return

    with open(events_path, "r", newline="", encoding="utf-8") as file:
        event_count = sum(1 for _ in file) - 1

    event = {
        "event_id": f"EVT-{event_count + 1:06d}",
        "claim_id": claim_id,
        "event_type": event_type,
        "event_time": datetime.now().isoformat(timespec="seconds"),
        "details": details,
    }

    with open(events_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "event_id",
                "claim_id",
                "event_type",
                "event_time",
                "details",
            ],
        )
        writer.writerow(event)


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

    if result.get("eligibility") == "NEEDS_DOCUMENTS":
        missing_documents = [
            item.split(":", 1)[1]
            for item in result.get("decision_reason", "").split(";")
            if item.startswith("MISSING_DOCUMENTS:")
        ]

        result["document_request"] = {
            "status": "PENDING",
            "missing_documents": missing_documents,
            "message": (
                "Please submit the missing documents "
                "to continue claim assessment."
            ),
        }

    log_claim_event(
        claim_id=claim_id,
        event_type="CLAIM_ASSESSED",
        details=(
            f"Eligibility: {result.get('eligibility')}; "
            f"Reason: {result.get('decision_reason')}"
        ),
    )

    if result.get("document_request"):
        log_claim_event(
            claim_id=claim_id,
            event_type="DOCUMENTS_REQUESTED",
            details=", ".join(
                result["document_request"]["missing_documents"]
            ),
        )

    return result, 200
