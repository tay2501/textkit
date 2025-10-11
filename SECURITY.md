# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in the Text Processing Toolkit, please report it responsibly by following these steps:

### How to Report

1. **Email**: Send details to the project maintainer (create a security advisory on GitHub)
2. **GitHub Security Advisory**: Use the [GitHub Security Advisory](https://github.com/tay2501/textkit/security/advisories/new) feature (preferred)

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker achieve by exploiting this vulnerability?
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Affected Components**: Which parts of the codebase are affected?
- **Suggested Fix**: If you have ideas on how to fix it (optional)
- **Environment Details**:
  - Python version
  - Operating system
  - Package version

### Example Report

```
Subject: [SECURITY] Potential Command Injection in CLI

Description:
The text transformation CLI may be vulnerable to command injection when
processing user-supplied input with special characters.

Impact:
An attacker could potentially execute arbitrary commands on the host system
by crafting malicious input strings.

Reproduction:
1. Install textkit version 0.1.0
2. Run: textkit text transform '/l' -i "$(malicious_command)"
3. Observe that the command is executed

Affected Components:
- components/text_core/core.py
- bases/text_processing/cli_interface/main.py

Environment:
- Python 3.12
- Windows 11
- textkit 0.1.0
```

## Response Timeline

- **Initial Response**: Within 48 hours of report submission
- **Status Update**: Within 5 business days with assessment of the vulnerability
- **Fix Timeline**: Depends on severity (see below)

### Severity Levels

| Severity | Response Time | Description |
|----------|--------------|-------------|
| **Critical** | 24-48 hours | Remote code execution, data loss, privilege escalation |
| **High** | 3-7 days | Information disclosure, authentication bypass |
| **Medium** | 14-30 days | Denial of service, minor information leaks |
| **Low** | 30-60 days | Low-impact issues, theoretical vulnerabilities |

## Security Update Process

1. **Verification**: We verify and reproduce the reported vulnerability
2. **Assessment**: Determine severity and impact scope
3. **Fix Development**: Create and test a fix in a private repository
4. **Coordination**: Coordinate disclosure timeline with reporter
5. **Release**: Release security update and publish advisory
6. **Disclosure**: Publicly disclose vulnerability details after fix is available

## Security Best Practices for Users

### Encryption & Sensitive Data

- **Never** store encryption keys in source code or configuration files committed to version control
- Use environment variables or secure key management systems for sensitive data
- Avoid processing untrusted encrypted data without validation

### Input Validation

- Always validate and sanitize user input before processing
- Be cautious when using the CLI with data from untrusted sources
- Use the `--no-clipboard` flag when processing sensitive data to avoid clipboard exposure

### File Operations

- Be careful when processing files from untrusted sources
- Verify file permissions and ownership before processing
- Use absolute paths when possible to avoid directory traversal issues

### Dependencies

- Keep the Text Processing Toolkit and its dependencies up to date
- Regularly run `uv sync --upgrade` to update dependencies
- Review security advisories for dependencies using tools like:
  - `pip-audit` (recommended)
  - OSV Scanner
  - GitHub Dependabot alerts

### Network Security

- If extending the toolkit with network features, always use HTTPS
- Validate and sanitize all data received from network sources
- Implement proper timeout and rate limiting

## Known Security Considerations

### Cryptographic Operations

The `crypto_engine` component uses the `cryptography` library for encryption/decryption:

- **Algorithm**: Uses Fernet (symmetric encryption based on AES-128-CBC and HMAC)
- **Key Derivation**: Keys should be generated using `Fernet.generate_key()`
- **Limitations**:
  - Not suitable for encrypting large files (>100MB)
  - Keys must be stored securely by the user
  - No built-in key rotation mechanism

### Character Encoding

The encoding transformation features:

- May expose sensitive data through error messages
- Should not be used for security-critical encoding transformations
- UTF-8 BOM handling may cause unexpected behavior with certain file types

### Clipboard Operations

- Clipboard operations may expose data to other processes
- Use `--no-clipboard` flag for sensitive operations
- Clipboard data persists after program exit

## Security Testing

We perform the following security checks on every commit:

- **CodeQL Analysis**: Automated code scanning for security vulnerabilities
- **Dependency Scanning**: OSV Scanner, pip-audit for known vulnerabilities
- **Static Analysis**: Bandit security linter for Python-specific issues
- **SAST**: Semgrep for pattern-based security analysis

## Security-Related Configuration

### Recommended `pyproject.toml` settings for users:

```toml
[tool.bandit]
exclude_dirs = ["/test", "/tests", "/.venv"]
skips = []  # Don't skip any tests

[tool.bandit.assert_used]
skips = ["*_test.py", "test_*.py"]
```

## Hall of Fame

We recognize and thank security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers will be listed here after disclosure -->

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [GitHub Security Advisories](https://github.com/tay2501/textkit/security/advisories)
- [Cryptography Library Documentation](https://cryptography.io/)

## Contact

For security-related questions that don't constitute a vulnerability report, you can:

- Open a discussion in [GitHub Discussions](https://github.com/tay2501/textkit/discussions)
- Refer to our [Contributing Guidelines](CONTRIBUTING.md) if available

---

**Last Updated**: 2025-10-11

This security policy is subject to change. Please check back regularly for updates.
