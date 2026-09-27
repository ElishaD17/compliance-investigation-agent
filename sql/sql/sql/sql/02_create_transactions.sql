CREATE OR REPLACE TABLE
  `compliance-agent-509701.compliance_analytics.pharmacy_transactions`
AS
SELECT
  FORMAT('TXN-%05d', n) AS transaction_id,
  DATE_ADD(DATE '2026-01-01', INTERVAL MOD(n, 180) DAY) AS transaction_date,
  FORMAT('PHARM-%03d', 1 + MOD(n, 20)) AS pharmacy_id,
  FORMAT('PAT-%04d', 1 + MOD(n * 7, 120)) AS patient_id,
  IF(MOD(n, 53) = 0, NULL, FORMAT('PROV-%03d', 1 + MOD(n * 3, 45))) AS prescriber_id,
  FORMAT('DRUG-%03d', 1 + MOD(n, 30)) AS drug_id,
  1 + MOD(n * 3, 90) AS quantity,
  CAST(
    IF(MOD(n, 37) = 0, 650, 15 + MOD(n * 17, 180))
    AS NUMERIC
  ) AS claim_amount,
  IF(MOD(n, 41) = 0, 'REVERSED', 'PAID') AS claim_status,
  'SYNTHETIC_DEMO' AS source_system
FROM UNNEST(GENERATE_ARRAY(1, 500)) AS n;