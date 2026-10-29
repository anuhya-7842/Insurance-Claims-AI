# AI Prompt History — Insurance Claims AI Workflow

## Purpose and Transparency

This document records AI assistance associated with the development of the Insurance Claims AI Workflow project, including planning, Python implementation, synthetic data generation, debugging, testing, database checks, and documentation.

**Important:** Some entries may be reconstructed examples rather than exact original prompts. They must not be presented as a complete verbatim transcript. Historical prompts that cannot be recovered should be identified as unavailable. Only prompts actually used should be included in the final submission.

## 1. Requirements and Design

### Prompt 1 — Break down the challenge

Help me break down the Insurance Claims AI Workflow challenge into manageable tasks. Identify the core requirements, expected outputs, validation checks, and deliverables. Keep the implementation achievable within a 72-hour individual project.

### Prompt 2 — Plan the architecture
Suggest a simple Python project structure with a data generator, claim assessment engine, service layer, application entry point, tests, and documentation. Avoid unnecessary frameworks and dependencies.

### Prompt 3 — Define the claim workflow
Explain a claim workflow covering submission, input validation, policy and coverage checks, document requirements, eligibility assessment, reserve calculation, settlement checks, and audit-event recording.

### Prompt 4 — Identify edge cases
List important insurance claim edge cases, including inactive policies, missing documents, invalid amounts, coverage-limit violations, duplicate paid settlements, and inconsistent references between records.

## 2. Synthetic Data Generation

### Prompt 5 — Design the data generator
Help design a Python data generator for synthetic insurance data containing customers, policies, coverages, incidents, claims, claim items, documents, adjusters, assessments, reserves, settlements, claim events, and ground-truth records.

### Prompt 6 — Maintain consistent identifiers
Suggest readable and unique identifier formats for policies, claims, documents, assessments, settlements, incidents, and claim events. Ensure related records reference the correct identifiers.

### Prompt 7 — Generate reproducible data
Explain how to use a fixed random seed so the generator produces the same dataset each time. Describe how to verify reproducibility by comparing generated file hashes.

### Prompt 8 — Validate generated records
Suggest validation checks for missing fields, duplicate primary keys, invalid references, unexpected null values, incorrect record counts, and inconsistent relationships between CSV files.

### Prompt 9 — Handle monetary precision
Review a reserve calculation that uses a claimed amount, deductible, and coverage limit. Ensure the result is not negative, does not exceed the coverage limit, and is rounded to two decimal places.

## 3. Claim Assessment Engine

### Prompt 10 — Implement deterministic eligibility rules
Help design a Python claim assessment engine using explicit, testable rules rather than an LLM making final eligibility decisions. Consider policy status, coverage limits, incident dates, missing documents, and claim amounts.

### Prompt 11 — Handle missing documents
Suggest a way to compare the required documents for a claim against the documents provided. Return a clear list of missing documents and indicate when additional information is required.

### Prompt 12 — Detect duplicate settlements
Help implement a rule that checks whether a claim has multiple settlements with status `PAID`. If more than one paid settlement exists, flag the claim for manual review and add a reason code. Do not delete or modify payment records automatically.

### Prompt 13 — Structure assessment results
Suggest a consistent structure for returning claim assessment results, including claim ID, eligibility decision, decision reason, missing documents, reserve amount, and review flags. Handle invalid input clearly.

### Prompt 14 — Separate business rules from service logic
Review the separation between claim assessment rules and the service layer. Explain how the service should call the assessment engine, return the result, and record audit events without duplicating business logic.

## 4. Debugging and Partial Code Review

### Prompt 15 — Investigate a failed test
A Python test is failing in the claim assessment engine. Explain the assertion failure, inspect the relevant rule, suggest the smallest appropriate fix, and add a regression test. Do not assume the expected result is correct without checking the requirements.

**Actual failure:** Add the real test output if available.

### Prompt 16 — Investigate data inconsistencies
The data validation script reports an inconsistency between related CSV files. Help trace the issue by checking primary keys, foreign keys, duplicate identifiers, missing references, and unexpected null values.

**Actual failure:** Add the real validation output if available.

### Prompt 17 — Investigate a PowerShell error
A Python command fails in Windows PowerShell. Help interpret the exact error, check the working directory and virtual environment, and suggest one diagnostic command at a time.

**Actual failure:** Add the actual PowerShell error if available.

### Prompt 18 — Review a partial reserve calculation
Review this Python code:

```python
reserve_amount = min(
    claimed_amount - deductible_amount,
    coverage_limit
)
```

Check how it behaves when the claimed amount is below the deductible, when amounts are negative, and when monetary values have more than two decimal places. Suggest the smallest safe correction.

### Prompt 19 — Review audit-event logging
Review this code fragment:

```python
if log_events:
    log_claim_event(
        claim_id=claim_id,
        event_type="CLAIM_ASSESSED",
        details=(
            f"Eligibility: {result.get('eligibility')}; "
            f"Reason: {result.get('decision_reason')}"
        ),
    )
```

Explain how to record a document-request event when documents are missing. Ensure runtime logging does not overwrite the original generated audit data.

## 5. Application and Database

### Prompt 20 — Verify the local environment
Explain how to verify the Python version and confirm that commands are running inside the project's virtual environment on Windows.

### Prompt 21 — Inspect SQLite tables
Suggest a simple way to verify that the SQLite database contains all expected tables and that its records correspond to the generated data.

### Prompt 22 — Check database integrity
Explain how to run a SQLite foreign-key integrity check and interpret the results. Identify what should be investigated if invalid references are reported.

### Prompt 23 — Preserve generated data
Suggest a safe approach for keeping baseline generated claim events separate from runtime audit events. Avoid silently overwriting the original generated data.

## 6. Testing and Verification

### Prompt 24 — Create assessment tests
Suggest pytest cases for eligible claims, ineligible claims, missing documents, invalid amounts, inactive policies, coverage-limit violations, and duplicate paid settlements. Each test should check a specific expected outcome.

### Prompt 25 — Run the test suite
Explain how to run the pytest suite from the repository root and interpret the results. If a test fails, help isolate the cause before modifying unrelated code.

### Prompt 26 — Verify data reproducibility
Describe a repeatable method to regenerate the synthetic data and compare SHA-256 hashes of generated CSV files. Explain what matching and differing hashes indicate.

### Prompt 27 — Validate all generated data
Explain how to run the data validation module and check record counts, identifiers, required columns, foreign-key consistency, and important edge cases.

## 7. Documentation and Submission

### Prompt 28 — Improve the README
Review the README for setup instructions, project structure, data-generation commands, testing, validation, design decisions, limitations, and AI-use transparency. Ensure documented filenames and commands match the actual repository.

### Prompt 29 — Document the data schema
Help create a data dictionary describing each generated CSV file, its columns, identifiers, relationships, and important field meanings. Verify the documentation against the actual schema.

### Prompt 30 — Perform a final submission review
Create a final checklist for a public GitHub repository containing a Python insurance claims workflow. Include clean-environment setup, tests, data validation, database integrity, reproducibility, secret scanning, documentation accuracy, AI-use disclosure, and known limitations.

## Prompt Recording Fields

For each verified prompt, record the following where possible:

- **AI tool:** ChatGPT or the actual tool used.
- **Date:** The date of the interaction, if known.
- **Prompt:** The exact original prompt.
- **Purpose:** What task the prompt supported.
- **Outcome:** The code, test, documentation, or decision affected.
- **Verification:** How the suggestion was checked.

## Limitations and Disclosure

Do not invent historical prompts, AI responses, tracebacks, failed commands, or debugging sessions to make this record look complete.

Where a real error occurred, record the actual error message, the change made, and the verification performed. If an example describes a possible error that never occurred, do not present it as an actual debugging incident.

The application uses deterministic Python business rules for claim decisions. AI assistance during development should be distinguished from AI functionality inside the running application.

The final record should reflect the actual tools used, the prompts that can be recovered, any missing historical records, and the developer's own review and testing.
