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
├── data/                 # Generated insurance datasets
├── docs/
│   └── data_dictionary.md
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
| GET | `/api/claims/<claim_id>/assess` | Assesses a specific insurance claim |
| POST | `/api/claims/assess` | Assesses a claim using a JSON request body |

### Example: Assess a Claim

```http
GET /api/claims/CLM-2026-000001/assess
```

Example response:

```json
{
  "claim_id": "CLM-2026-000001",
  "eligibility": "NEEDS_REVIEW",
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
2. Whether the policy is cancelled.
3. Whether the claim type matches the policy product.
4. Whether mandatory documents are available.
5. Whether the claimed amount exceeds the coverage limit.
6. Whether another claim exists for the same policy and incident.
7. Whether multiple paid settlements exist for the same claim.
8. Whether paid settlements exceed the coverage limit.

Claims requiring further investigation are marked `NEEDS_REVIEW`.

## Run Tests

Execute the automated test suite:

```bash
python -m pytest -v
```

The test suite covers eligible claims, policy validity, missing documents, coverage limits, claim type mismatches, duplicate claims, duplicate payments, and settlement-limit violations.

## Data Documentation

Refer to [`docs/data_dictionary.md`](docs/data_dictionary.md) for descriptions of the generated datasets, their fields, and relationships.

## Future Improvements

- Add a web-based dashboard for claim assessment and review.
- Integrate machine learning models for anomaly detection.
- Add authentication, role-based access control, and audit logging.
- Expand API integration and reporting capabilities.

## Author

**Dhathri Anuhya Devarampati**

GitHub: [anuhya-7842](https://github.com/anuhya-7842)

---

*This project uses synthetic insurance data for development and demonstration purposes.*
