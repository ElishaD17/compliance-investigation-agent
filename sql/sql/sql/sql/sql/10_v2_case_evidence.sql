CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v2_case_evidence`
AS
WITH pharmacy_baseline AS (
  SELECT
    q.pharmacy_id,
    COUNT(*) AS routine_claim_count,
    ROUND(AVG(q.claim_amount), 2) AS routine_avg_amount
  FROM `compliance-agent-509701.compliance_analytics.v2_claim_quality` AS q
  LEFT JOIN `compliance-agent-509701.compliance_analytics.v2_case_candidates` AS c
    ON q.transaction_id = c.transaction_id
  WHERE q.quality_status = 'PASS'
    AND q.claim_status = 'PAID'
    AND q.claim_amount < 500
    AND c.case_id IS NULL
  GROUP BY q.pharmacy_id
)
SELECT
  c.case_id,
  c.rule_ids,
  c.rule_count,
  q.transaction_id,
  q.transaction_date,
  q.pharmacy_id,
  q.patient_id,
  q.prescriber_id,
  q.drug_id,
  q.quantity,
  q.claim_amount,
  q.claim_status,
  q.quality_status,
  b.routine_claim_count,
  b.routine_avg_amount,
  ROUND(
    SAFE_DIVIDE(q.claim_amount, b.routine_avg_amount), 2
  ) AS amount_vs_pharmacy_average,
  r.prior_transaction_id,
  r.prior_transaction_date,
  DATE_DIFF(
    q.transaction_date, r.prior_transaction_date, DAY
  ) AS days_since_prior
FROM `compliance-agent-509701.compliance_analytics.v2_case_candidates` AS c
JOIN `compliance-agent-509701.compliance_analytics.v2_claim_quality` AS q
  ON c.transaction_id = q.transaction_id
LEFT JOIN pharmacy_baseline AS b
  ON q.pharmacy_id = b.pharmacy_id
LEFT JOIN `compliance-agent-509701.compliance_analytics.v2_repeat_fill_flags` AS r
  ON c.transaction_id = r.transaction_id;