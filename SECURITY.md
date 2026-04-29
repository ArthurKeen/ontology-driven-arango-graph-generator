# Security Policy

## Reporting a Vulnerability

Please report security issues privately before opening a public issue. If this repository is hosted on GitHub, use GitHub's private vulnerability reporting feature when available. Otherwise, contact the maintainer through the repository owner's preferred private channel.

Include:

- A description of the issue and affected files or commands.
- Steps to reproduce the issue.
- Any known impact or exposure.
- Whether credentials, private endpoints, or customer data may be involved.

## Credential Handling

This project expects real ArangoDB credentials to live only in a local `.arango` file. That file is ignored by git. The committed `.arango.example` file must contain placeholders only.

Before publishing a release:

- Search for committed credentials, tokens, private endpoints, and local absolute paths.
- Rotate any credential that was ever committed, even if it has since been removed.
- Confirm command output masks passwords.
