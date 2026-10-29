
# Insurance Claims AI - Data Dictionary

All dates use ISO 8601 format: YYYY-MM-DD.
All monetary amounts use USD.
All primary keys are unique, immutable strings unless specified otherwise.
Required fields cannot be null.

## 1. Customer
- customer_id: string, PK, required, unique.
- full_name: string, required.
- email: string, required, unique.
- phone: string, optional.
- created_at: datetime, required.

## 2. Policy
- policy_id: string, PK, required, unique.
- customer_id: string, FK → Customer, required.
- product_type: enum (AUTO, PROPERTY, HEALTH, TRAVEL, LIABILITY), required.
- start_date: date, required.
- end_date: date, required, must be on or after start_date.
- cancellation_date: date, nullable; required when status is CANCELLED.
- status: enum (ACTIVE, EXPIRED, CANCELLED), required.
- premium_amount: decimal, USD, non-negative.
- created_at: datetime, required.

## 3. Coverage
- coverage_id: string, PK, required, unique.
- policy_id: string, FK → Policy, required.
- coverage_type: string, required.
- limit_amount: decimal, USD, positive.
- deductible_amount: decimal, USD, non-negative and no greater than limit_amount.
- exclusions: JSON array, required.
- effective_from: date, required.
- effective_to: date, required, on or after effective_from.

## 4. Claim
- claim_id: string, PK, required, unique.
- policy_id: string, FK → Policy, required.
- incident_id: string, FK → Incident, required.
- claim_date: date, required.
- claimed_amount: decimal, USD, positive.
- claim_type: enum (AUTO, PROPERTY, HEALTH, TRAVEL, LIABILITY), required.
- status: enum (SUBMITTED, UNDER_REVIEW, NEEDS_DOCUMENTS, APPROVED, REJECTED, SETTLED), required.
- issue_type: string, optional; identifies deliberately injected anomalies.
- created_at: datetime, required.

## 5. ClaimItem
- claim_item_id: string, PK, required, unique.
- claim_id: string, FK → Claim, required.
- description: string, required.
- amount: decimal, USD, positive.
- quantity: integer, positive.
- item_total: decimal, USD; amount multiplied by quantity.

## 6. Document
- document_id: string, PK, required, unique.
- claim_id: string, FK → Claim, required.
- document_type: enum (CLAIM_FORM, INCIDENT_REPORT, INVOICE, ID_PROOF, PHOTO), required.
- received_at: datetime, optional until received.
- status: enum (RECEIVED, MISSING, INVALID), required.
- file_reference: string, optional; synthetic reference only.
- created_at: datetime, required.

## 7. Incident
- incident_id: string, PK, required, unique.
- customer_id: string, FK → Customer, required.
- incident_date: date, required.
- incident_type: enum (AUTO, PROPERTY, HEALTH, TRAVEL, LIABILITY), required.
- description: string, required.
- location: string, optional; synthetic location.
- issue_type: string, optional.

## 8. Adjuster
- adjuster_id: string, PK, required, unique.
- full_name: string, required.
- specialization: enum (AUTO, PROPERTY, HEALTH, TRAVEL, LIABILITY, GENERAL), required.
- active: boolean, required.
- max_open_claims: integer, positive.

## 9. Assessment
- assessment_id: string, PK, required, unique; format `ASN-<claim_id>-001` (sequential suffix for multiple assessments per claim).
- claim_id: string, FK → Claim, required.
- adjuster_id: string, FK → Adjuster, optional until assigned.
- eligibility: enum (ELIGIBLE, INELIGIBLE, NEEDS_REVIEW, NEEDS_DOCUMENTS), required.
- recommended_amount: decimal, USD, non-negative.
- decision_reason: string, required.
- assessed_at: datetime, required.
- rules_version: string, required.

## 10. Reserve
- reserve_id: string, PK, required, unique.
- claim_id: string, FK → Claim, required.
- amount: decimal, USD, non-negative.
- reserve_type: enum (INITIAL, ADJUSTMENT, RELEASE), required.
- created_at: datetime, required.
- reason: string, required.

## 11. Settlement
- settlement_id: string, PK, required, unique; format `SET-<claim_id>-001` (sequential suffix for multiple settlements per claim).
- claim_id: string, FK → Claim, required.
- amount: decimal, USD, non-negative.
- settlement_date: date, optional until settled.
- status: enum (PENDING, APPROVED, PAID, REJECTED), required.
- payment_reference: string, optional; identifies the payment transaction.
- created_at: datetime, required.

## Relationships and Cardinality

- Customer 1:N Policy.
- Customer 1:N Incident.
- Policy 1:N Coverage.
- Policy 1:N Claim.
- Incident 1:N Claim; duplicate-incident claims can reference the same incident.
- Claim 1:N ClaimItem.
- Claim 1:N Document.
- Claim 1:N Assessment.
- Adjuster 1:N Assessment; an assessment may be unassigned.
- Claim 1:N Reserve.
- Claim 1:N Settlement; multiple records allow payment history and duplicate-payment detection.
- Customer to Policy: each policy belongs to exactly one customer; a customer may have multiple policies.
- Policy to Coverage: each coverage belongs to one policy; a policy may have multiple coverages.
- Claim to Incident: each claim references one incident; multiple claims may reference the same incident.
- Claim to Assessment, Reserve, and Settlement: each record references one claim; a claim may have multiple records of each type.
- Assessment to Adjuster: an assessment may be unassigned; when assigned, it references one adjuster.

## Key and Relationship Constraints

- Every primary key must be unique and non-null.
- Every foreign key must reference an existing parent record, except explicitly optional relationships.
- Each Policy references one Customer.
- Each Coverage references one Policy.
- Each Claim references one Policy and one Incident.
- Each ClaimItem and Document references one Claim.
- Each Assessment references one Claim and may reference an Adjuster.
- Each Reserve and Settlement references one Claim.
- Multiple Assessments, Reserves, and Settlements may exist for a Claim to preserve history.
- Foreign-key relationships must be validated before claim assessment or settlement routing.

## Lifecycle and Audit Requirements

- Policy coverage is valid only when the incident date falls within policy and coverage effective dates and the policy is not cancelled.
- Missing or invalid mandatory documents require NEEDS_DOCUMENTS or NEEDS_REVIEW.
- Every assessment records its rule version and decision reason.
- Reserves and settlements must be reconciled with coverage limits and deductibles.
- State changes must be appended to an event history rather than silently overwriting prior decisions.
- Deliberate anomalies must be labelled in a separate ground-truth dataset, never used as model input features.
- All generated identities and relationships must be deterministic and reproducible.
