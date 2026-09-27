CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v_claim_quality`
AS
WITH claims AS (
  SELECT
    *,
    COUNT(*) OVER (PARTITION BY transaction_id) AS transaction_id_count
  FROM `compliance-agent-509701.compliance_analytics.pharmacy_transactions`
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