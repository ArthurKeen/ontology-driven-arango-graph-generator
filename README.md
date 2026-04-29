# Ontology-Driven ArangoDB Graph Generator

Tools for transforming OWL/RDF ontologies and sample RDF data into ArangoDB graph databases using RDF Preserving Transformation (RPT), Property Graph Transformation (PGT), and Labeled Property Graph Transformation (LPGT) patterns.

## Features

- Transform any OWL/RDF ontology into ArangoDB-backed graph models.
- Manage multiple local or cloud ArangoDB clusters with a git-ignored `.arango` file.
- Start and inspect local Docker-backed ArangoDB instances from the CLI.
- Validate documentation, environment setup, and portable unit tests in CI.

## Quick Start

```bash
git clone https://github.com/<owner>/ontology-driven-arango-graph-generator.git
cd ontology-driven-arango-graph-generator

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

docker compose up -d
cp .arango.example .arango

python tools/setup_environment.py
python tools/transform_ontology.py --list-clusters
python tools/transform_ontology.py --cluster local_dev --test-connection
```

Run a transformation with your own files:

```bash
python tools/transform_ontology.py --cluster local_dev --patterns pgt \
  --owl /path/to/ontology.owl \
  --ttl /path/to/sample_data.ttl
```

## Cluster Configuration

Real credentials belong only in your local `.arango` file. Start from the committed example:

```bash
cp .arango.example .arango
```

```yaml
clusters:
  local_dev:
    type: "docker"
    name: "Local Development"
    container_name: "ontology-arango"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "change-me"
    database: "graph_ontology"

default: "local_dev"
```

## Transformation Patterns

- `rpt`: RDF Preserving Transformation for retaining RDF semantics.
- `pgt`: Property Graph Transformation for common traversal and analytics workloads.
- `lpgt`: Labeled Property Graph Transformation for richer labels and schema flexibility.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest
python tools/validate_documentation.py
```

Live ArangoDB transformations require a configured `.arango` file and ontology input files. Unit tests are portable and do not require a running database.

## Documentation

- [Documentation Index](docs/README.md)
- [Cluster Management Guide](docs/CLUSTER_MANAGEMENT.md)
- [API Reference](docs/API_REFERENCE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)
- [Tools Documentation](tools/README.md)

## Security

Do not commit `.arango`, `.env`, real cloud endpoints for private infrastructure, or credentials. If a credential has ever been committed, rotate it before publishing or tagging a release.

Report vulnerabilities using the guidance in [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, tests, and pull request expectations.

## License

This project is licensed under the [MIT License](LICENSE).
