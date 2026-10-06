# RDS IAM Policy Risk Review

## 1. Intended use

The supplied use case is to create user-specific roles for RDS database access:

- **ReadOnly:** SELECT only
- **CRUB:** SELECT, INSERT, UPDATE, DELETE
- **Admin:** full DDL + DML

## 2. Major issue — IAM permissions are not database SQL permissions

The supplied IAM policies control what AWS API operations a principal can perform against Amazon RDS. They do not, by themselves, create SQL-level SELECT/INSERT/UPDATE/DELETE privileges inside a database engine.

Therefore the requested application roles should be implemented as two layers:

1. AWS IAM controls — who can administer/describe/connect to RDS-related AWS resources.
2. Database-native controls — who can execute SELECT, INSERT, UPDATE, DELETE and DDL inside the database.

This distinction is critical.

## 3. Admin policy risks

The supplied Admin role includes:

```text
rds:*
```

on `Resource: *`.

**Risk:** this is effectively unrestricted RDS control from the AWS API perspective.

An administrator with this permission may create, modify, delete or reconfigure RDS resources, subject to other account-level controls.

**Mitigation:**
- replace `rds:*` with the exact required API actions;
- restrict resources where the API supports resource-level permissions;
- separate database administration from infrastructure administration;
- require MFA/strong authentication for privileged human access;
- use privileged access workflows and logging.

## 4. CRUB role risk

The supplied CRUB policy also grants:

```text
rds:*
```

on all resources.

This is inconsistent with the stated business requirement of CRUD database access.

**Risk:** a role intended to perform data operations could instead receive AWS-level administrative capability.

**Mitigation:** remove `rds:*` from the CRUB IAM role. Use database-native users/roles for SELECT/INSERT/UPDATE/DELETE, and give the IAM role only the minimum AWS permissions needed for the connection/authentication mechanism and operational workflow.

## 5. ReadOnly role

The ReadOnly policy contains `rds:Describe*` and related EC2 describe actions.

This is much closer to an infrastructure-observer role, but it does not itself guarantee SELECT-only database access.

**Mitigation:** create a database-native read-only role with SELECT privileges on the required schemas/tables. Keep AWS API read permissions separate from database data-plane privileges.

## 6. Service-linked role creation

The Admin role can create service-linked roles for:

- `rds.amazonaws.com`
- `rds.application-autoscaling.amazonaws.com`

This can be legitimate for RDS automation, but it should be restricted to the administrative workflow that actually needs it.

## 7. Performance Insights and DevOps Guru

The policy grants Performance Insights metrics/report access and DevOps Guru RDS-related permissions.

These can be useful operationally, but should be justified against the actual monitoring requirement.

**Mitigation:** keep monitoring permissions in a separate monitoring role if they are not required by database administrators.

## 8. Recommended role separation

| Role | AWS layer | Database layer |
|---|---|---|
| ReadOnly | Minimal RDS/connection/describe permissions | SELECT only |
| CRUB | Minimal connection/required AWS permissions | SELECT, INSERT, UPDATE, DELETE |
| Admin | Narrow RDS administration permissions | Full approved DDL + DML |

## 9. Additional controls

- Use AWS IAM Identity Center/federation for human access.
- Prefer short-lived credentials.
- Use Secrets Manager where database credentials are required.
- Encrypt RDS storage and backups.
- Encrypt client connections with TLS.
- Enable CloudTrail for AWS API activity.
- Enable database auditing appropriate to the engine.
- Use security groups to restrict network access to approved application/admin sources.
- Use separate AWS accounts for production and non-production where practical.
- Apply deletion protection and backup controls to critical databases.
- Periodically review privileged access.

## 10. Risk rating

| Risk | Rating | Mitigation |
|---|---|---|
| `rds:*` for Admin on `*` | Critical/High | Least-privilege action/resource policy |
| `rds:*` for CRUB | Critical/High | Remove AWS admin capability; implement DB-native CRUD |
| ReadOnly IAM mistaken for SELECT-only DB access | High | Database-native SELECT role |
| Monitoring privileges mixed with admin role | Medium | Separate monitoring role |
| Service-linked role creation | Medium | Restrict to required administration workflow |

## 11. Overall conclusion

The requested business model is sound, but the supplied IAM policies do not correctly implement the stated database privilege model. In particular, the CRUB role should not receive unrestricted `rds:*`.

The recommended design is a layered least-privilege model: AWS IAM controls access to AWS/RDS management capabilities, while database-native roles enforce SELECT/CRUD/DDL privileges inside the database.
