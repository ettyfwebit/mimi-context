# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of mimi-context seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT report security vulnerabilities through public GitHub issues.

Instead, please report them via:

1. **Email**: Send details to [security@your-domain.com](mailto:security@your-domain.com)
2. **GitHub Security Advisories**: Use the "Report a vulnerability" button in the Security tab
3. **Private disclosure**: Contact the maintainer directly

### What to include in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline:

- **Initial Response**: Within 48 hours
- **Triage**: Within 7 days
- **Resolution**: Varies based on severity and complexity

### Security Update Process:

1. Vulnerability assessment and impact analysis
2. Development of patch/fix
3. Testing and validation
4. Coordinated disclosure (if applicable)
5. Release of security update
6. Public security advisory

## Security Best Practices

### For Contributors:

- Never commit secrets, API keys, or credentials
- Use environment variables for configuration
- Follow secure coding practices
- Run security scans before submitting PRs
- Keep dependencies updated

### For Users:

- Always use the latest stable version
- Keep your deployment environment secure
- Use strong authentication mechanisms
- Monitor security advisories
- Enable automatic security updates

## Security Features

This project implements several security measures:

- Automated dependency vulnerability scanning
- Secrets scanning in CI/CD pipeline
- Container security scanning
- Code quality and security linting
- Regular security audits

## Security Contacts

- **Primary**: [security@your-domain.com](mailto:security@your-domain.com)
- **Maintainer**: [@ettyfwebit](https://github.com/ettyfwebit)

## Acknowledgments

We thank the following researchers and security professionals who have helped improve the security of this project:

<!-- Add acknowledgments here as they come in -->

---

_Last updated: September 2025_
