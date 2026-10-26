# Release Checklist

Use this checklist before tagging a release.

## Security

- CI's `secrets` job (gitleaks over the full history) passes.
- Any ArangoDB credential that was ever committed or shared in logs has been rotated.
- Public examples use placeholders such as `example.arangodb.cloud`.

## Quality

```bash
ruff format --check .
ruff check .
pytest
ARANGO_TEST_ENDPOINT=http://localhost:8529 ARANGO_TEST_PASSWORD=change-me pytest -m integration
```

- All CI jobs pass on `main`: lint, test (Python 3.10–3.13), integration, secrets.
- The README quick start works from a fresh clone.

## Versioning

- Bump `__version__` in `ontology_graph_generator/__init__.py`.
- Move the `Unreleased` entries in `CHANGELOG.md` under the new version and date.
- Tag `vX.Y.Z` on the release commit and push the tag to every remote.
