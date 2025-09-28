---
name: Security Vulnerability
about: Report a security vulnerability (use this template for non-critical security issues only)
title: '[SECURITY] '
labels: ['security', 'high-priority']
assignees: ''
---

⚠️ **IMPORTANT**: For critical security vulnerabilities, please do NOT use this public issue template. Instead, please report privately via:
- Email: security@your-domain.com
- GitHub Security Advisories (preferred)
- Direct contact with maintainers

## Security Issue Type

- [ ] Authentication bypass
- [ ] Authorization issue
- [ ] Data exposure
- [ ] Injection vulnerability (SQL, XSS, etc.)
- [ ] Insecure configuration
- [ ] Dependency vulnerability
- [ ] Other (please specify)

## Affected Components

- [ ] Backend (mimi-core)
- [ ] Frontend (mimi-web)
- [ ] Database
- [ ] Authentication system
- [ ] API endpoints
- [ ] File upload functionality
- [ ] Configuration files

## Severity Assessment

- [ ] Critical (immediate action required)
- [ ] High (should be fixed soon)
- [ ] Medium (should be addressed)
- [ ] Low (minor security improvement)

## Description

Provide a clear description of the security issue. Include:
- What is vulnerable?
- How could it be exploited?
- What data or functionality is at risk?

## Steps to Reproduce

1. 
2. 
3. 

## Impact

Describe the potential impact if this vulnerability were exploited:
- What data could be accessed?
- What actions could an attacker perform?
- Who would be affected?

## Affected Versions

- Version: [e.g. 1.0.0, all versions, latest]
- Component: [e.g. backend, frontend, both]

## Suggested Fix

If you have suggestions for how to fix this issue, please share them:

## Additional Context

- Have you seen this issue exploited in the wild?
- Are there any known workarounds?
- Any relevant security research or CVE references?

## Environment Details

- Deployment type: [local, staging, production]
- Authentication method: [if relevant]
- Network setup: [if relevant]

## Checklist

- [ ] I have confirmed this is a legitimate security concern
- [ ] I have not disclosed this publicly anywhere else
- [ ] I understand this will be handled with appropriate priority
- [ ] I have provided sufficient detail for investigation

---

**Note**: The maintainers will review this issue and may move it to a private security advisory if needed. Thank you for helping keep our project secure!