CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v2_claim_quality`
AS
WITH claims AS (
  SELECT
    *,
    COUNT(*) OVER (PARTITION BY transaction_id) AS transaction_id_count
  FROM `compliance-agent-509701.compliance_analytics.pharmacy_transactions_v2`
)
SELECT
  *,
  CASE
    WHEN transaction_id_count > 1 THEN 'DUPLICATE_ID'
    WHEN prescriber_id IS NULL THEN 'MISSING_PRESCRIBER'
    WHEN quantity <= 0 THEN 'INVALID_QUANTITY'
    WHEN claim_amount <= 0 THEN 'INVALID_AMOUNT'
    ELSE 'PASS'
  END AS quality_status
FROM claims;

CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v2_high_amount_flags`
AS
SELECT
  transaction_id,
  transaction_date,
  pharmacy_id,
  patient_id,
  prescriber_id,
  drug_id,
  quantity,
  claim_amount,
  claim_status,
  'R001_HIGH_CLAIM_AMOUNT' AS rule_id
FROM `compliance-agent-509701.compliance_analytics.v2_claim_quality`
WHERE quality_status = 'PASS'
  AND claim_status = 'PAID'
  AND claim_amount >= 500;