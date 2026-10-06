# Test Cases

| Test | Purpose | Expected Result |
|---|---|---|
| 1 | Empty/clean target with scanners installed | JSON report; PASS if all scanners report clean |
| 2 | Fake secret in test file | Gitleaks finding; overall FAIL |
| 3 | Known vulnerable dependency | pip-audit finding; overall FAIL |

The tests in `tests/test_security_scan.py` additionally verify JSON parsing and safe handling when scanner binaries are missing.
