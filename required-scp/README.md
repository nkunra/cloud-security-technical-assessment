# Required SCP — Restrict AWS Services to eu-west-1

## Objective

The assessment asks for an AWS Organizations Service Control Policy that restricts use of AWS services to the `eu-west-1` region.

## Design

The SCP uses:

- `Effect: Deny`
- `NotAction` for global/control-plane APIs that do not use regional endpoints in the same way
- `aws:RequestedRegion`
- `StringNotEquals` against `eu-west-1`

The result is a guardrail: actions requested against other AWS regions are denied.

## Important operational consideration

An SCP does not grant permissions. It sets the maximum permissions available to principals in affected accounts/OUs. IAM policies must still grant the required permissions.

The exception list is intentionally limited to common global/control-plane services/actions. Before production deployment, the organisation should validate every required global service against its actual AWS architecture.

## Deployment process

1. Save the policy as `region-restriction-scp.json`.
2. Validate the JSON syntax.
3. In AWS Organizations, create a new SCP.
4. Paste/upload the policy.
5. Give it a descriptive name such as `Deny-Regions-Except-EU-West-1`.
6. Attach it first to a non-production test OU/account.
7. Test approved `eu-west-1` operations.
8. Test an operation in another region and confirm it is denied.
9. Review CloudTrail/CloudWatch evidence.
10. Roll out to production OUs using controlled change management.

## Example CLI validation

```bash
python -m json.tool region-restriction-scp.json
```

## Test expectations

### Allowed

An IAM principal with the necessary IAM permissions should be able to use a regional service in:

```text
eu-west-1
```

### Denied

The same principal should receive an explicit deny when attempting a covered regional action in:

```text
eu-west-2
us-east-1
af-south-1
```

## Caveats

Some AWS services and global services have special regional behaviour. The `NotAction` exception list should therefore be validated against the organisation's actual workloads before production enforcement.

For high-assurance production use, test the SCP with AWS IAM Access Analyzer, CloudTrail and representative workloads before broad OU attachment.
