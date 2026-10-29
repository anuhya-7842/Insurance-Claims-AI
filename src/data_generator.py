
import json
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 20261022
POLICY_COUNT = 2000
CLAIM_COUNT = 1000
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"

PRODUCT_TYPES = ["AUTO", "PROPERTY", "HEALTH", "TRAVEL", "LIABILITY"]
CLAIM_TYPES = PRODUCT_TYPES
POLICY_STATUSES = ["ACTIVE", "EXPIRED", "CANCELLED"]
DOCUMENT_TYPES = [
    "CLAIM_FORM",
    "INCIDENT_REPORT",
    "INVOICE",
    "ID_PROOF",
    "PHOTO",
]


def make_id(prefix, number, width=6):
    return f"{prefix}{number:0{width}d}"


def generate_data(
    policy_count=POLICY_COUNT,
    claim_count=CLAIM_COUNT,
    seed=SEED,
):
    rng = random.Random(seed)
    today = date(2026, 10, 27)

    customers = []
    policies = []
    coverages = []
    incidents = []
    claims = []
    claim_items = []
    documents = []
    adjusters = []
    assessments = []
    reserves = []
    settlements = []
    ground_truth = []
    events = []

    # Step 1: Generate customers (master records).
    customer_count = max(1, (policy_count + 1) // 2)

    for i in range(1, customer_count + 1):
        customers.append({
            "customer_id": make_id("CUS-", i),
            "full_name": f"Customer {i:05d}",
            "email": f"customer{i:05d}@example.test",
            "phone": None,
            "created_at": "2026-01-01T09:00:00",
        })

    # Step 2: Generate policies and coverage records.
    for i in range(1, policy_count + 1):
        product = PRODUCT_TYPES[(i - 1) % len(PRODUCT_TYPES)]
        customer_id = make_id("CUS-", ((i - 1) // 2) + 1)

        start = date(2025, 1, 1) + timedelta(
            days=rng.randint(0, 600)
        )
        end = start + timedelta(days=rng.randint(180, 730))

        status = rng.choices(
            POLICY_STATUSES,
            weights=[70, 25, 5],
            k=1,
        )[0]

        if status == "EXPIRED":
            end = min(end, today - timedelta(days=1))
            start = min(start, end)

        if status == "ACTIVE":
            start = min(start, today)
            end = max(end, today + timedelta(days=1))

        cancellation_date = None

        if status == "CANCELLED":
            end = min(end, today - timedelta(days=1))
            start = min(start, end)
            cancellation_date = end

        policy_id = f"POL-{product}-2026-{i:06d}"
        limit_amount = rng.choice([5000, 10000, 25000, 50000])
        deductible = rng.choice([100, 250, 500, 1000])
        deductible = min(deductible, limit_amount)

        policies.append({
            "policy_id": policy_id,
            "customer_id": customer_id,
            "product_type": product,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "cancellation_date": (
                cancellation_date.isoformat()
                if cancellation_date is not None
                else None
            ),
            "status": status,
            "premium_amount": round(rng.uniform(200, 2500), 2),
            "created_at": "2026-01-01T09:00:00",
        })

        coverages.append({
            "coverage_id": make_id("COV-", i),
            "policy_id": policy_id,
            "coverage_type": product,
            "limit_amount": limit_amount,
            "deductible_amount": deductible,
            "exclusions": json.dumps(["INTENTIONAL_DAMAGE"]),
            "effective_from": start.isoformat(),
            "effective_to": end.isoformat(),
        })

    # Step 3: Generate adjusters.
    for i in range(1, 21):
        adjusters.append({
            "adjuster_id": make_id("ADJ-", i),
            "full_name": f"Adjuster {i:03d}",
            "specialization": (
                PRODUCT_TYPES[(i - 1) % len(PRODUCT_TYPES)]
            ),
            "active": True,
            "max_open_claims": 100,
        })

    # Step 4: Generate claims and dependent records.
    # Dates and amounts are derived from policy and incident data.
    for i in range(1, claim_count + 1):
        policy_number = ((i - 1) % policy_count) + 1
        policy = policies[policy_number - 1]
        coverage = coverages[policy_number - 1]

        claim_id = f"CLM-2026-{i:06d}"
        incident_id = make_id("INC-", i)
        claim_type = policy["product_type"]

        start = date.fromisoformat(policy["start_date"])
        end = date.fromisoformat(policy["end_date"])

        valid_start = max(start, date(2026, 1, 1))
        valid_end = min(end, today)

        issue_type = "NONE"

        if valid_start <= valid_end:
            incident_date = valid_start + timedelta(
                days=rng.randint(0, (valid_end - valid_start).days)
            )
        else:
            incident_date = today

        # Claim 1: incident before policy start.
        if i == 1:
            incident_date = start - timedelta(days=1)
            issue_type = "INCIDENT_BEFORE_POLICY_START"

        # Claim 2: policy cancelled before the incident.
        if i == 2:
            policy["status"] = "CANCELLED"
            incident_date = min(end, today)
            cancellation_date = date(2026, 3, 31)

            if cancellation_date < start:
                cancellation_date = start
                incident_date = start + timedelta(days=1)

            policy["cancellation_date"] = (
                cancellation_date.isoformat()
            )
            issue_type = "POLICY_CANCELLED"

        claimed_amount = round(
            rng.uniform(250, coverage["limit_amount"] * 0.95), 2
        )

        # Claim 3: duplicate incident within the policy period.
        if i == 3:
            incident_id = make_id("INC-", 2)
            incident_date = date(2026, 4, 1)
            issue_type = "DUPLICATE_INCIDENT"

        # Claim 4: amount exceeds the policy limit.
        if i == 4:
            claimed_amount = coverage["limit_amount"] * 1.5
            issue_type = "CLAIM_OVER_LIMIT"

        incident = {
            "incident_id": incident_id,
            "customer_id": policy["customer_id"],
            "incident_date": incident_date.isoformat(),
            "incident_type": claim_type,
            "description": f"Synthetic {claim_type.lower()} incident",
            "location": None,
            "issue_type": (
                "DUPLICATE_INCIDENT" if i == 3 else "NONE"
            ),
        }

        existing_incident = next(
            (
                row for row in incidents
                if row["incident_id"] == incident_id
            ),
            None,
        )

        if existing_incident is None:
            incidents.append(incident)
        elif i == 3:
            existing_incident["incident_date"] = incident_date.isoformat()
        # Claim 8: duplicate claim scenario.
        if i == 8:
            issue_type = "DUPLICATE_CLAIM"


        claims.append({
            "claim_id": claim_id,
            "policy_id": (
                claims[-1]["policy_id"] if i == 8
                else policy["policy_id"]
            ),
            "incident_id": (
                claims[-1]["incident_id"] if i == 8
                else incident_id
            ),
            "claim_date": (
                claims[-1]["claim_date"] if i == 8
                else (
                    incident_date + timedelta(days=rng.randint(0, 20))
                ).isoformat()
            ),
            "claimed_amount": (
                claims[-1]["claimed_amount"] if i == 8
                else round(claimed_amount, 2)
            ),
            "claim_type": (
                claims[-1]["claim_type"] if i == 8
                else claim_type
            ),
            "status": "SUBMITTED",
            "issue_type": issue_type,
            "created_at": "2026-10-27T09:00:00",
        })

        claim_items.append({
            "claim_item_id": make_id("ITM-", i),
            "claim_id": claim_id,
            "description": f"Synthetic {claim_type.lower()} expense",
            "amount": round(claimed_amount, 2),
            "quantity": 1,
            "item_total": round(claimed_amount, 2),
        })

        required_docs = [
            "CLAIM_FORM",
            "INCIDENT_REPORT",
            "INVOICE",
        ]

        if i == 5:
            required_docs.remove("INVOICE")

        for j, document_type in enumerate(required_docs, start=1):
            documents.append({
                "document_id": f"DOC-{claim_id}-{j:03d}",
                "claim_id": claim_id,
                "document_type": document_type,
                "received_at": (
                    None if i == 5 and document_type == "INVOICE"
                    else "2026-10-27T09:05:00"
                ),
                "status": (
                    "MISSING" if i == 5 and document_type == "INVOICE"
                    else "RECEIVED"
                ),
                "file_reference": None,
                "created_at": "2026-10-27T09:05:00",
            })

        adjuster_id = make_id("ADJ-", ((i - 1) % 20) + 1)

        # Preliminary reserve cannot exceed the coverage limit.
        reserve_amount = round(
            min(
                max(0, claimed_amount - coverage["deductible_amount"]),
                coverage["limit_amount"],
            ),
            2,
        )

        assessments.append({
            "assessment_id": f"ASN-{claim_id}-001",
            "claim_id": claim_id,
            "adjuster_id": adjuster_id,
            "eligibility": "NEEDS_REVIEW",
            "recommended_amount": reserve_amount,
            "assessed_at": "2026-10-27T09:10:00",
            "decision_reason": "Pending deterministic rules evaluation",
            "rules_version": "1.0",
        })

        reserves.append({
            "reserve_id": make_id("RSV-", i),
            "claim_id": claim_id,
            "amount": reserve_amount,
            "reserve_type": "INITIAL",
            "created_at": "2026-10-27T09:10:00",
            "reason": "Preliminary reserve estimate",
        })
        # Generate deterministic settlement records.
        # Every 10th claim receives a settlement.
        if i % 10 == 0:
            settlements.append({
                "settlement_id": f"SET-{claim_id}-001",
                "claim_id": claim_id,
                "amount": reserve_amount,
                "settlement_date": "2026-10-27",
                "status": "PAID",
                "payment_reference": f"PAY-{i:06d}",
                "created_at": "2026-10-27T09:15:00",
            })

        # Claim 6: settlement exceeds the coverage limit.
        if i == 6:
            settlements.append({
                "settlement_id": f"SET-{claim_id}-001",
                "claim_id": claim_id,
                "amount": round(coverage["limit_amount"] + 100, 2),
                "settlement_date": "2026-10-27",
                "status": "PAID",
                "payment_reference": f"PAY-{i:06d}",
                "created_at": "2026-10-27T09:15:00",
            })

        # Claim 7: simulate a duplicate payment.
        if i == 7:
            for payment_number in (1, 2):
                settlements.append({
                    "settlement_id": (
                        f"SET-{claim_id}-{payment_number:03d}"
                    ),
                    "claim_id": claim_id,
                    "amount": reserve_amount,
                    "settlement_date": "2026-10-27",
                    "status": "PAID",
                    "payment_reference": (
                        f"PAY-{i:06d}-{payment_number}"
                    ),
                    "created_at": "2026-10-27T09:15:00",
                })

        events.append({
            "event_id": make_id("EVT-", i),
            "claim_id": claim_id,
            "event_type": "CLAIM_SUBMITTED",
            "event_time": "2026-10-27T09:00:00",
            "details": "Claim created by synthetic data generator",
        })

        # Ground truth is kept separately from input features.
        ground_truth_issue = issue_type

        if i == 5:
            ground_truth_issue = "MISSING_MANDATORY_DOCUMENT"
        elif i == 6:
            ground_truth_issue = "SETTLEMENT_EXCEEDS_COVERAGE_LIMIT"
        elif i == 7:
            ground_truth_issue = "DUPLICATE_PAYMENT"
        elif i == 8:
            ground_truth_issue = "DUPLICATE_CLAIM"

        expected_decisions = {
            "INCIDENT_BEFORE_POLICY_START": "INELIGIBLE",
            "POLICY_CANCELLED": "INELIGIBLE",
            "DUPLICATE_INCIDENT": "NEEDS_REVIEW",
            "CLAIM_OVER_LIMIT": "NEEDS_REVIEW",
            "MISSING_MANDATORY_DOCUMENT": "NEEDS_DOCUMENTS",
            "SETTLEMENT_EXCEEDS_COVERAGE_LIMIT": "NEEDS_REVIEW",
            "DUPLICATE_PAYMENT": "NEEDS_REVIEW",
            "DUPLICATE_CLAIM": "NEEDS_REVIEW",
        }

        if ground_truth_issue != "NONE":
            ground_truth.append({
                "claim_id": claim_id,
                "issue_type": ground_truth_issue,
                "expected_decision": expected_decisions[ground_truth_issue],
            })

    # Step 5: Export every entity to its own CSV file.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "customers": customers,
        "policies": policies,
        "coverages": coverages,
        "incidents": incidents,
        "claims": claims,
        "claim_items": claim_items,
        "documents": documents,
        "adjusters": adjusters,
        "assessments": assessments,
        "reserves": reserves,
        "settlements": settlements,
        "claim_events": events,
        "ground_truth": ground_truth,
    }

    for name, rows in datasets.items():
        pd.DataFrame(rows).to_csv(
            OUTPUT_DIR / f"{name}.csv",
            index=False,
        )
    primary_keys = {
        "customers": "customer_id",
        "policies": "policy_id",
        "coverages": "coverage_id",
        "incidents": "incident_id",
        "claims": "claim_id",
        "claim_items": "claim_item_id",
        "documents": "document_id",
        "adjusters": "adjuster_id",
        "assessments": "assessment_id",
        "reserves": "reserve_id",
        "settlements": "settlement_id",
        "claim_events": "event_id",
        "ground_truth": "claim_id",
    }

    foreign_keys = {
        "policies": [("customer_id", "customers", "customer_id")],
        "coverages": [("policy_id", "policies", "policy_id")],
        "incidents": [("customer_id", "customers", "customer_id")],
        "claims": [
            ("policy_id", "policies", "policy_id"),
            ("incident_id", "incidents", "incident_id"),
        ],
        "claim_items": [("claim_id", "claims", "claim_id")],
        "documents": [("claim_id", "claims", "claim_id")],
        "assessments": [
            ("claim_id", "claims", "claim_id"),
            ("adjuster_id", "adjusters", "adjuster_id"),
        ],
        "reserves": [("claim_id", "claims", "claim_id")],
        "settlements": [("claim_id", "claims", "claim_id")],
        "claim_events": [("claim_id", "claims", "claim_id")],
        "ground_truth": [("claim_id", "claims", "claim_id")],
    }

    # Export all datasets to a SQLite-compatible SQL seed file.
    sql_path = OUTPUT_DIR / "insurance_claims.sql"
    database_path = OUTPUT_DIR / "insurance_claims.db"
    database_path.unlink(missing_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        # Create tables with primary and foreign key constraints.
        for name, rows in datasets.items():
            df = pd.DataFrame(rows)
            column_definitions = []

            for column in df.columns:
                if pd.api.types.is_integer_dtype(df[column].dtype):
                    sql_type = "INTEGER"
                elif pd.api.types.is_float_dtype(df[column].dtype):
                    sql_type = "REAL"
                else:
                    sql_type = "TEXT"

                definition = f'"{column}" {sql_type}'

                if primary_keys.get(name) == column:
                    definition += " PRIMARY KEY NOT NULL"

                column_definitions.append(definition)

            for child_column, parent_table, parent_column in foreign_keys.get(
                name, []
            ):
                column_definitions.append(
                    f'FOREIGN KEY ("{child_column}") '
                    f'REFERENCES "{parent_table}" ("{parent_column}")'
                )

            create_table_sql = (
                f'CREATE TABLE "{name}" '
                f'({", ".join(column_definitions)})'
            )
            connection.execute(create_table_sql)

        # Insert rows into the created tables.
        for name, rows in datasets.items():
            pd.DataFrame(rows).to_sql(
                name,
                connection,
                if_exists="append",
                index=False,
            )

        with sql_path.open("w", encoding="utf-8") as sql_file:
            sql_file.write("PRAGMA foreign_keys = ON;\n")
            for line in connection.iterdump():
                sql_file.write(line + "\n")

    summary = {
        name: len(rows)
        for name, rows in datasets.items()
    }

    (OUTPUT_DIR / "generation_summary.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "generated_at": "2026-10-27",
                "counts": summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Synthetic data generation completed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    generate_data()
