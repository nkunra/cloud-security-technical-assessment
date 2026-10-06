# SSM IAM Policy Risk Review

## 1. Intended use

The policy is intended for SSM-driven deployment from an Azure DevOps pipeline. The supplied architecture/use case states that commands/applications are deployed via SSM from Azure DevOps.

## 2. Positive controls already present

### Resource restriction for EC2 control actions

Start/stop/reboot/tag actions are restricted to the supplied `eu-west-1` EC2 instance ARN pattern.

### Tag-based command restriction

`ssm:SendCommand` to EC2 instances requires:

- `AutomationAllowed=true`
- `Application=Automated-Deployment-Dev`

This is a useful preventive control because the automation role should not be able to target arbitrary instances.

### Document restriction

`ssm:SendCommand` is restricted to a defined set of SSM documents rather than allowing every SSM document.

### High-risk SSM deny

The policy explicitly denies numerous operations such as `StartSession`, maintenance-window administration, patch-baseline administration, parameter writes, association changes and document changes.

This reduces the ability of the deployment identity to become an administration identity.

## 3. Key risks

### Risk 1 — S3 object access is too broad

The policy permits:

```text
arn:aws:s3:::*/*
```

for `GetObject` and `PutObject`.

**Risk:** the execution role can potentially read or write objects in buckets unrelated to this deployment.

**Mitigation:** restrict object access to the exact deployment bucket and prefix, for example:

```text
arn:aws:s3:::automated-deployment-bucket/dev/*
```

Also use separate read/write permissions if the workflow allows it.

**Outcome:** smaller blast radius if the role or pipeline is compromised.

### Risk 2 — S3 bucket permission is wildcarded by name

`GetBucketLocation` uses an `automated-deployment*` pattern.

**Mitigation:** reference the exact approved bucket ARN where practical and enforce bucket policy conditions.

### Risk 3 — Start/stop/reboot can cause availability impact

Even though these EC2 actions are scoped by ARN, an automation identity can still disrupt workloads if the tagging controls are bypassed or incorrectly applied.

**Mitigation:**
- use separate deployment and operational roles;
- require deployment-specific tags;
- use AWS Organizations SCP guardrails where appropriate;
- monitor CloudTrail for EC2 state changes;
- alert on unexpected use outside approved deployment windows.

### Risk 4 — `CreateTags` is a security boundary consideration

The role can change EC2 tags. Because tags are used by `ssm:SendCommand` as a control condition, allowing the same identity to freely manipulate those tags can create a potential privilege-escalation path.

**Mitigation:** do not allow the deployment role to modify the security-sensitive `AutomationAllowed` / `Application` tags, or use an explicit condition/key restriction on allowed tag keys and values. A separate provisioning process should establish trusted tags.

**Outcome:** prevents an automation identity from potentially granting itself additional command targets.

### Risk 5 — `ssm:SendCommand` is a powerful execution capability

Run Command can execute shell/PowerShell commands on managed instances. Even with document restrictions, this is effectively remote code execution on the permitted targets.

**Mitigation:**
- allow only approved documents;
- constrain target instances with tags;
- maintain change approval in Azure DevOps;
- log command invocation and CloudTrail activity;
- use short-lived federated credentials/OIDC rather than long-lived AWS access keys;
- separate development and production roles/accounts.

### Risk 6 — CloudWatch Logs permissions are broader than necessary

The policy permits creation and writing within the supplied log-group pattern.

**Mitigation:** pre-create the required log groups and reduce permissions where operationally possible. Use resource policies and retention controls.

### Risk 7 — Explicit deny maintenance is useful but should not be treated as complete least privilege

A large deny list can reduce selected high-risk actions, but the security model is strongest when the allow policy itself is narrowly scoped.

**Mitigation:** use allow-list design first; use denies as defence-in-depth.

## 4. Recommended control model

1. Azure DevOps authenticates using short-lived federated credentials.
2. The role is dedicated to a specific deployment purpose.
3. Deployment targets are restricted by trusted tags.
4. Approved SSM documents are explicitly enumerated.
5. S3 is restricted to one approved bucket/prefix.
6. Security-sensitive tags cannot be modified by the deployment role.
7. CloudTrail records IAM/SSM/EC2 activity.
8. GuardDuty/Security Hub/SIEM monitoring detects anomalous activity.
9. Production deployments use a separate AWS account/role from development.
10. Access is reviewed periodically.

## 5. Risk rating

| Risk | Initial rating | Recommended treatment |
|---|---|---|
| Broad S3 object access | High | Restrict to exact bucket/prefix |
| Tag-based privilege boundary | High | Separate trusted tagging/provisioning |
| SSM command execution | High | Approved documents + target restrictions + monitoring |
| EC2 state changes | Medium | Deployment role separation + monitoring |
| Broad logging permissions | Medium | Pre-create resources and reduce scope |
| Large deny-list dependence | Medium | Strengthen positive allow-list |

## 6. Overall conclusion

The policy has several good compensating controls, particularly resource scoping for EC2 actions, approved SSM documents, target tags and explicit high-risk SSM denies. The most important weaknesses are the wildcard S3 object permissions and the fact that the same role can manipulate EC2 tags that participate in its own SSM targeting boundary.

The policy should therefore be approved only after tightening those boundaries and confirming that the Azure DevOps authentication mechanism uses short-lived credentials.
