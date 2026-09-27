# Compliance Investigation Agent

Portfolio project using entirely synthetic pharmacy claims to demonstrate data quality checks, explainable investigation rules, and AI-assisted case review.

## Current progress

- BigQuery dataset: `compliance-agent-509701.compliance_analytics`
- 500 synthetic pharmacy transactions
- Data quality view: 491 PASS, 9 MISSING_PRESCRIBER
- First investigation rule: 13 paid claims flagged for amount >= $500
- Pharmacy comparison evidence view

A flag is a prompt for human review, not a finding of fraud.

## Run the SQL

Run the files in `sql/` in numerical order in the BigQuery query editor.

## Planned work

Python and LangGraph investigation workflow, Gemini evidence summaries,
human review and audit records, and a Power BI dashboard.