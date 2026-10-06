# Risk Review

This section reviews the two IAM policy requests supplied in the assessment.

## Scope

### SSM

The supplied SSM execution-role policy is intended to support deployment of commands/applications through SSM from an Azure DevOps pipeline. The assessment material includes EC2 describe/start/stop/reboot/tag actions, SSM command/document access, CloudWatch Logs, S3 access, and a broad explicit deny list for higher-risk SSM operations.

### RDS

The supplied RDS role design provides:
- Admin — full DDL + DML
- CRUB — SELECT, INSERT, UPDATE, DELETE
- ReadOnly — SELECT only

The supplied Admin policy includes `rds:*`, application autoscaling, CloudWatch, SNS, Performance Insights, service-linked role creation, and DevOps Guru permissions.

See the detailed assessment in `SSM-risk-review.md` and `RDS-risk-review.md`.
