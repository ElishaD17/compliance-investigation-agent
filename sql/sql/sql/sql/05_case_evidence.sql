CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v_case_evidence`
AS
WITH pharmacy_baseline AS (
  SELECT
    pharmacy_id,
    COUNT(*) AS routine_claim_count,
    ROUND(AVG(claim_amount), 2) AS routine_avg_amount
  FROM `compliance-agent-509701.compliance_analytics.v_claim_quality`
  WHERE quality_status = 'PASS'
    AND claim_status = 'PAID'
    AND claim_amount < 500
  GROUP BY pharmacy_id
)
SELECT
  f.*,
  b.routine_claim_count,
  b.routine_avg_amount,
  ROUND(
    SAFE_DIVIDE(f.claim_amount, b.routine_avg_amount),
    1
  ) AS amount_vs_pharmacy_average
FROM `compliance-agent-509701.compliance_analytics.v_investigation_flags` AS f
LEFT JOIN pharmacy_baseline AS b
  USING (pharmacy_id);