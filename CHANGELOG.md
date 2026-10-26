# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Code moved from `tools/` scripts to the installable `ontology_graph_generator` package. The commands are `ontology-transform` and `ontology-env`, or `python -m ontology_graph_generator`.
- `--owl` is now required. `--owl` and `--ttl` files that do not exist are errors rather than being silently skipped.
- Graphs are no longer dropped on every run. Re-runs update documents in place; pass `--overwrite` to replace graphs.
- Ontology formats are detected automatically, including Turtle files with an `.owl` extension (`--rdf-format` to force one).
- Requires Python 3.10+, arango-rdf 2.x, and python-arango 8.x.
- Copyright holder is ArangoDB GmbH (license remains MIT).

### Added

- `--graph-name`, `--database` (also for clusters), `--endpoint`, `--overwrite`, `--verbose`, `--version`.
- `password_env` in `.arango` and `ARANGO_PASSWORD` for direct connections.
- Configuration validation when `.arango` is loaded.
- Docker auto-start waits until ArangoDB responds, instead of a fixed sleep.
- Example ontology and data in `examples/`.
- Integration tests against a live ArangoDB, and a gitleaks secret scan, in CI.

### Removed

- `--password`, `--host`, and `--port` flags (use `--endpoint` with `ARANGO_PASSWORD`).
- `--setup-deps`, and dependency installation from `ontology-env` (use `pip install -e .`).
- `quick_start.py`, `demo_cluster_management.py`, `test_credentials.py`, `validate_documentation.py`, `requirements.txt`, `requirements.lock`, and the unused `owlready2` dependency.

### Fixed

- Users without `_system` access can load into existing databases.
- Docker container lookup matches the exact container name.
- A `default` cluster that doesn't exist is reported instead of silently replaced.

## [0.1.0]

- Initial public release.
