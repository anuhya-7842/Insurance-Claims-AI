# Insurance Claims AI

An end-to-end insurance claims assessment workflow built with Python and Flask. The system validates insurance data, evaluates claim eligibility, calculates recommended claim amounts, and flags suspicious claims for manual review using rule-based decision-making.

## Features

- **Synthetic Data Generation:** Generates interconnected insurance datasets for customers, policies, claims, incidents, coverage, documents, reserves, settlements, and more.
- **Data Validation:** Checks data integrity, primary keys, foreign key relationships, required fields, and business constraints.
- **Claims Assessment:** Evaluates policy validity, coverage dates, claim types, required documents, and claim amounts.
- **Fraud and Anomaly Checks:** Flags duplicate claims, duplicate payments, and settlements exceeding coverage limits.
- **REST API:** Provides endpoints to assess individual claims and check application health.
- **Automated Testing:** Includes unit tests for key claims assessment rules.

## Tech Stack

- **Language:** Python
- **Backend:** Flask
- **Data Processing:** Pandas
- **API:** REST API
- **Testing:** Pytest
- **Version Control:** Git and GitHub

## Project Structure

```text
Insurance-Claims-AI/
├── data/                       # Generated insurance datasets
│   ├── *.csv                   # Claims, policies, customers, etc.
│   ├── generation_summary.json
│   ├── validation_summary.json
│   ├── insurance_claims.db
│   └── insurance_claims.sql    # SQL export of the datasets
├── docs/
│   ├── data_dictionary.md
│   └── source_manifest.json
├── src/
│   ├── __init__.py
│   ├── data_generator.py
│   ├── validate_data.py
│   ├── claims_engine.py
│   └── claim_service.py
├── tests/
│   └── test_claims_engine.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/anuhya-7842/Insurance-Claims-AI.git
cd Insurance-Claims-AI
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate the datasets

```bash
python -m src.data_generator
```

### 5. Validate the data

```bash
python -m src.validate_data
```

### 6. Start the application

```bash
python app.py
```

The Flask application runs locally at `http://127.0.0.1:5000`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns application information and available endpoints |
| GET | `/health` | Checks application health |
| GET | `/api/claims/review` | Lists claims requiring review or missing documents |
| GET | `/api/claims/<claim_id>/assess` | Assesses a specific insurance claim |
| POST | `/api/claims/assess` | Assesses a claim using a JSON request body |
| GET | `/api/claims/<claim_id>/settlement-route` | Checks whether a claim is ready for settlement review and blocks unsafe routing cases |

### Example: Assess a Claim

```http
GET /api/claims/CLM-2026-000001/assess
```

Example response:

```json
{
  "claim_id": "CLM-2026-000001",
  "eligibility": "INELIGIBLE",
  "recommended_amount": 0,
  "preliminary_reserve": 0,
  "decision_reason": "INCIDENT_BEFORE_POLICY_START",
  "rules_version": "1.0"
}
```

*The response above illustrates the expected format; actual results depend on the generated dataset and assessment rules.*

## Claims Assessment Rules

The claims engine checks:

1. Whether the incident occurred within the policy's validity period.
2. Whether the policy was cancelled on or before the incident date.
3. Whether the claim type matches the policy product.
4. Whether mandatory documents are available.
5. Whether the claimed amount exceeds the coverage limit.
6. Whether another claim exists for the same policy and incident.
7. Whether the same incident is associated with claims under different policies.
8. Whether multiple paid settlements exist for the same claim.
9. Whether paid settlements exceed the coverage limit.

Claims requiring further investigation are marked `NEEDS_REVIEW`.

## Run Tests

Execute the automated test suite:

```bash
python -m pytest -v
```

The test suite covers eligible claims, policy validity and cancellation dates, missing mandatory documents, coverage limits, claim type mismatches, duplicate claims and incidents, duplicate paid settlements, settlement-limit violations, document requests, and settlement routing safeguards.

## Data Reproducibility

The synthetic data generator uses a fixed random seed (`20261022`) to produce repeatable datasets. The generator supports configurable policy and claim counts.

### Generate the datasets

```bash
python -m src.data_generator
```

The generator exports the datasets in the following formats:

- **CSV:** Individual files for all 13 datasets.
- **JSON:** Generation and data validation summaries.
- **SQL:** `data/insurance_claims.sql`, containing SQL statements to recreate the exported tables and data.
- **SQLite:** `data/insurance_claims.db`, a database containing all 13 datasets.

### Validate the generated data

```bash
python -m src.validate_data
```

The validation process checks dataset integrity and business constraints before the data is used by the claims workflow. The project also includes automated tests for claims assessment, duplicate-payment detection, missing-document handling, and settlement routing.

### Verify the SQLite database

The SQLite database can be inspected using Python's built-in `sqlite3` module. The generated database contains 13 tables, including claims, policies, coverages, documents, assessments, reserves, settlements, claim events, and ground-truth anomaly labels.

The current baseline contains 2,000 policies and 1,000 claims.

**Reproducibility note:** Run the generator with the same seed and configuration to reproduce the synthetic datasets. Verify reproducibility by comparing output checksums across separate runs. Database file checksums may vary even when the underlying data is equivalent.

## Data Documentation

Refer to [`docs/data_dictionary.md`](docs/data_dictionary.md) for descriptions of the generated datasets, their fields, and relationships.

## Future Improvements

- Add a web-based dashboard for claim assessment and review.
- Integrate machine learning models for anomaly detection.
- Add authentication, role-based access control, and audit logging.
- Expand API integration and reporting capabilities.

## Author

**Venkata Dhathri Anuhya Devarampati**

GitHub: [anuhya-7842](https://github.com/anuhya-7842)

---

*This project uses synthetic insurance data for development and demonstration purposes.*
