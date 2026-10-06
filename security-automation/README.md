# Security Automation

## Objective

Create one repeatable command that orchestrates four security checks and produces a unified result:

1. **SAST** — Semgrep
2. **Dependency vulnerability audit** — pip-audit
3. **Secrets detection** — Gitleaks
4. **Infrastructure-as-Code scanning** — Checkov

This directly addresses the assessment requirement to run multiple security tools and aggregate their results into a pass/fail decision.

## Usage

```bash
python3 security-scan.py --path ./app --format json
```

or on Windows:

```powershell
python security-scan.py --path .\app --format json
```

## Tool installation examples

```bash
pip install semgrep pip-audit checkov
```

Install Gitleaks using the official release/package appropriate for your operating system.

The script deliberately reports a missing scanner as `NOT_INSTALLED` and fails the overall result. This avoids creating a false impression that the repository passed a control that was never executed.

## Example test cases

### Test 1 — clean/small project

```bash
mkdir app
python3 security-scan.py --path ./app --format json
```

Expected behaviour: a structured JSON report is returned. If all four tools are installed and find no issues, `overall_status` is `PASS`.

### Test 2 — intentional secret

Create a test file containing a fake high-entropy token, for example:

```text
AWS_ACCESS_KEY_ID=AKIAEXAMPLE1234567890
```

Run:

```bash
python3 security-scan.py --path ./app --format json
```

Expected behaviour: the secrets scanner should identify the test secret and the aggregate status should be `FAIL`.

**Important:** use only a fake test value. Never put a real credential in this public repository.

### Test 3 — vulnerable dependency

Create a temporary Python requirements file with an intentionally old/vulnerable package version and run the dependency scan.

Expected behaviour: `pip-audit` reports the vulnerable dependency and the aggregate status becomes `FAIL`.

## Design decisions

- Standard Python library is used for orchestration to minimise dependencies.
- `subprocess` executes security tools.
- Each scanner receives an independent result.
- Scanner exit code and parsed findings are retained for auditability.
- Missing tools are treated as failures rather than skipped.
- A five-minute timeout limits a runaway scanner.
- JSON is used as the machine-readable interchange format.

## Limitations

Scanner output schemas differ between products. This implementation preserves each scanner's native JSON under `findings` instead of pretending that all scanners expose identical finding fields.
