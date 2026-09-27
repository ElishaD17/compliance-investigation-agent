CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v2_repeat_fill_flags`
AS
WITH paid_quality_claims AS (
  SELECT
    transaction_id,
    transaction_date,
    pharmacy_id,
    patient_id,
    drug_id,
    quantity,
    claim_amount
  FROM `compliance-agent-509701.compliance_analytics.v2_claim_quality`
  WHERE quality_status = 'PASS'
    AND claim_status = 'PAID'
),
ordered_claims AS (
  SELECT
    *,
    LAG(transaction_id) OVER (
      PARTITION BY patient_id, pharmacy_id, drug_id, quantity, claim_amount
      ORDER BY transaction_date, transaction_id
    ) AS prior_transaction_id,
    LAG(transaction_date) OVER (
      PARTITION BY patient_id, pharmacy_id, drug_id, quantity, claim_amount
      ORDER BY transaction_date, transaction_id
    ) AS prior_transaction_date
  FROM paid_quality_claims
)
SELECT
  transaction_id,
  prior_transaction_id,
  transaction_date,
  prior_transaction_date,
  pharmacy_id,
  patient_id,
  drug_id,
  quantity,
  claim_amount,
  'R002_REPEAT_FILL' AS rule_id
FROM ordered_claims
WHERE prior_transaction_date IS NOT NULL
  AND DATE_DIFF(transaction_date, prior_transaction_date, DAY) BETWEEN 0 AND 7;