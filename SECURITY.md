# Security Policy

## Reporting a Vulnerability

Please report security issues privately rather than in a public issue. Use GitHub's private vulnerability reporting on this repository: **Security** tab → **Report a vulnerability**.

Include:

- A description of the issue and affected files or commands.
- Steps to reproduce the issue.
- Any known impact or exposure.
- Whether credentials, private endpoints, or customer data may be involved.

## Credential Handling

- Real ArangoDB credentials live only in a local, git-ignored `.arango` file, or in environment variables referenced by `password_env` or `ARANGO_PASSWORD`.
- The committed `.arango.example` contains placeholders only.
- Passwords are never accepted as command-line flags, and connection output masks them.
- CI scans the full git history for secrets with gitleaks.
- Rotate any credential that was ever committed, even if it has since been removed from history.
