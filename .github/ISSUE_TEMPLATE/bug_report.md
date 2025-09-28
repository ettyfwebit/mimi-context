---
name: Bug Report
about: Create a report to help us improve
title: "[BUG] "
labels: ["bug", "needs-triage"]
assignees: ""
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Screenshots

If applicable, add screenshots to help explain your problem.

## Environment

**Backend (mimi-core):**

- OS: [e.g. macOS, Linux, Windows]
- Python version: [e.g. 3.10]
- FastAPI version: [e.g. 0.104.1]
- Database: [e.g. SQLite, PostgreSQL]

**Frontend (mimi-web):**

- OS: [e.g. macOS, Windows]
- Browser: [e.g. chrome, safari]
- Node.js version: [e.g. 18.x]
- React version: [e.g. 18.2.0]

**Deployment:**

- Environment: [e.g. local, staging, production]
- Docker version (if applicable): [e.g. 20.10.x]

## Error Messages

```
Paste any error messages or stack traces here
```

## Configuration

**Backend environment variables (remove sensitive data):**

```
APP_ENV=development
VECTOR_BACKEND=qdrant
AGENT_BACKEND=openai
```

**Frontend environment variables (remove sensitive data):**

```
VITE_MIMI_API_BASE=http://localhost:8081
```

## Additional Context

Add any other context about the problem here. Include:

- When did this start happening?
- Does it happen consistently?
- Have you tried any workarounds?
- Any recent changes to your setup?

## Logs

If applicable, include relevant log output:

```
Paste relevant logs here
```

## Checklist

- [ ] I have searched existing issues to ensure this bug hasn't been reported
- [ ] I can reproduce this bug consistently
- [ ] I have provided all necessary information above
- [ ] I have removed any sensitive information from this report
