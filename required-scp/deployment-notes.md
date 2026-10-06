# SCP Deployment Notes

## Security rationale

Region restrictions reduce data-residency risk, limit accidental resource deployment outside the approved operating region, and reduce the geographic blast radius of unauthorised activity.

## Rollout strategy

### Phase 1
Attach to a dedicated test account/OU.

### Phase 2
Run application and infrastructure test suites.

### Phase 3
Review denied API calls and identify legitimate global-service dependencies.

### Phase 4
Apply to non-production.

### Phase 5
Apply to production following change approval and rollback planning.

## Rollback

Detach the SCP from the affected OU/account if the policy blocks a legitimate business workload. Investigate the denied API call before modifying the exception list.
