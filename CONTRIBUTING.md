# Contributing

Thanks for helping improve the Ontology-Driven ArangoDB Graph Generator.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

cp .arango.example .arango
docker compose up -d
```

Unit tests do not need a database. Docker and `.arango` are only needed for live transformations and integration tests.

## Checks

Run these before opening a pull request:

```bash
ruff format --check .
ruff check .
pytest

# With ArangoDB running from docker compose
ARANGO_TEST_ENDPOINT=http://localhost:8529 ARANGO_TEST_PASSWORD=change-me pytest -m integration
```

CI also scans the full git history for secrets with gitleaks.

## Pull Request Guidelines

- Keep credentials, private endpoints, customer names, and local absolute paths out of commits.
- Update documentation when commands, config fields, or setup steps change. `tests/test_docs.py` fails if docs mention CLI flags that do not exist.
- Add or update tests for behavior changes.
- Add a line to the `Unreleased` section of `CHANGELOG.md`.
