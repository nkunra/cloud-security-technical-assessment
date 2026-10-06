# Cloud Security Technical Assessment

This repository contains the completed deliverables for the Cloud Security Technical Assessment.

## Assessment structure

- `security-automation/` — Python security scanning/orchestration tool
- `risk-review/` — IAM/security risk assessment for SSM and RDS
- `required-scp/` — AWS Organizations SCP restricting workloads to `eu-west-1`

## Security note

The assessment requires a public GitHub repository. No real passwords, API keys, access keys, tokens, private certificates, or production credentials are included.

## Quick review

The automation script is designed to run common security tools where they are installed and returns a unified JSON result with an overall PASS/FAIL decision.

See each folder's README for execution and deployment details.
