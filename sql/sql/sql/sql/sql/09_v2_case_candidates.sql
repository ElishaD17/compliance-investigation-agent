CREATE OR REPLACE VIEW
  `compliance-agent-509701.compliance_analytics.v2_case_candidates`
AS
WITH all_flags AS (
  SELECT transaction_id, rule_id
  FROM `compliance-agent-509701.compliance_analytics.v2_high_amount_flags`

  UNION ALL

  SELECT transaction_id, rule_id
  FROM `compliance-agent-509701.compliance_analytics.v2_repeat_fill_flags`
)
SELECT
  transaction_id AS case_id,
  transaction_id,
  ARRAY_AGG(DISTINCT rule_id ORDER BY rule_id) AS rule_ids,
  COUNT(DISTINCT rule_id) AS rule_count
FROM all_flags
GROUP BY transaction_id;