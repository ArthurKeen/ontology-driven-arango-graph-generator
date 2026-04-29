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

The unit test suite does not require a live ArangoDB instance. Use Docker and `.arango` only for manual connection tests or live transformations.

## Checks

Run these before opening a pull request:

```bash
ruff format --check .
ruff check .
pytest
python tools/validate_documentation.py
```

## Pull Request Guidelines

- Keep credentials, private endpoints, and local absolute paths out of commits.
- Update documentation when commands, config fields, or setup steps change.
- Add or update tests for behavior changes.
- Keep public examples generic and safe to copy.
