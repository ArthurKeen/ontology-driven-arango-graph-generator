# Release Checklist

Use this checklist before making the repository public or tagging a release.

## Security

- Rotate any ArangoDB credential that was ever committed or shared in logs.
- Confirm `.arango`, `.env`, and other local credential files are ignored.
- Run a secret-oriented search for passwords, tokens, private endpoints, and local absolute paths.
- Confirm public examples use placeholders such as `example.arangodb.cloud`.

## Quality

```bash
ruff format --check .
ruff check .
pytest
python tools/validate_documentation.py
```

## Repository Metadata

- Confirm `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md` are present.
- Confirm `README.md` quick start works for a new clone.
- Confirm `pyproject.toml`, `requirements.txt`, and any lock file are aligned.
- Confirm CI is passing on the release branch.

## Publishing

- Review `git status` for accidental local files.
- Tag the release only after CI passes.
- Do not publish until any previously exposed credentials have been rotated.
