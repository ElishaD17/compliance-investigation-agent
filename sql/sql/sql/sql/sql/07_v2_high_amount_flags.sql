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