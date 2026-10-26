# Ontology-Driven ArangoDB Graph Generator

[![CI](https://github.com/arango-solutions-org/ontology-driven-arango-graph-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/arango-solutions-org/ontology-driven-arango-graph-generator/actions/workflows/ci.yml)

A command-line tool that loads an OWL/RDF ontology, plus optional instance data, into ArangoDB as graphs. It supports three graph models: RDF-topology Preserving Transformation (RPT), Property Graph Transformation (PGT), and Labeled Property Graph Transformation (LPGT).

## Why use this instead of arango-rdf directly?

[arango-rdf](https://github.com/ArangoDB-Community/ArangoRDF) does the conversion itself. This project wraps it with what you need to run it repeatedly against real deployments:

- One command applies one or more patterns, each into its own named graph.
- Named connection profiles in a git-ignored `.arango` file switch between local Docker and cloud deployments. Passwords can come from environment variables.
- Stopped local Docker containers are started automatically, and the tool waits until ArangoDB is ready.
- Ontology formats are detected automatically, including Turtle saved with an `.owl` extension.
- Re-runs are idempotent. Existing graphs are replaced only when you ask with `--overwrite`.

## Quick Start

Requires Python 3.10+ and, for a local database, Docker.

```bash
git clone https://github.com/arango-solutions-org/ontology-driven-arango-graph-generator.git
cd ontology-driven-arango-graph-generator

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

docker compose up -d          # set ARANGO_PORT=18529 first if port 8529 is taken
cp .arango.example .arango

ontology-env                  # check the environment
ontology-transform --list-clusters
ontology-transform --cluster local_dev --test-connection
ontology-transform --cluster local_dev --owl examples/ontology.owl --ttl examples/sample_data.ttl
```

Open the ArangoDB web UI at http://localhost:8529 (user `root`, password `change-me`) and look at the `pgt_ontology_graph` graph in the `graph_ontology` database.

Run the transformation with your own files and several patterns:

```bash
ontology-transform --cluster local_dev --patterns rpt pgt lpgt \
  --owl /path/to/ontology.owl \
  --ttl /path/to/sample_data.ttl
```

Connect without a `.arango` file:

```bash
export ARANGO_PASSWORD=change-me
ontology-transform --endpoint http://localhost:8529 --owl examples/ontology.owl
```

## Transformation Patterns

| Pattern | Graph model | Collections created |
|---------|-------------|---------------------|
| `rpt` | RDF-topology Preserving Transformation: every triple becomes an edge, so the data can be converted back to RDF without loss. | `<graph>_URIRef`, `<graph>_BNode` and `<graph>_Literal` vertices; `<graph>_Statement` edges |
| `pgt` | Property Graph Transformation: resources are grouped by `rdf:type`, and literals become document attributes. | One vertex collection per class (e.g. `Employee`) and one edge collection per predicate (e.g. `worksFor`) |
| `lpgt` | Labeled Property Graph: all statements share one edge collection, with each edge labelled by its predicate (`_label`, `_uri`). | `Node` vertices for instances, `Class` and `Property` vertices for ontology terms; `Edge` edges |

Each pattern writes the graph `<pattern>_<graph-name>`; the default graph name is `ontology_graph`. PGT and LPGT collection names come from the ontology and are not prefixed, so load different ontologies into different databases (`--database`).

## Configuration

Real credentials belong only in your local `.arango` file, which is git-ignored. Start from the committed example:

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

  cloud_demo:
    type: "cloud"
    endpoint: "https://example.arangodb.cloud:8529"
    username: "demo_user"
    password_env: "ARANGO_CLOUD_DEMO_PASSWORD"

default: "local_dev"
```

See the [Cluster Management Guide](docs/CLUSTER_MANAGEMENT.md) for all fields.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest

# End-to-end tests against a running ArangoDB
ARANGO_TEST_ENDPOINT=http://localhost:8529 ARANGO_TEST_PASSWORD=change-me pytest -m integration
```

## Documentation

- [Documentation Index](docs/README.md)
- [Cluster Management Guide](docs/CLUSTER_MANAGEMENT.md)
- [API Reference](docs/API_REFERENCE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)
- [Changelog](CHANGELOG.md)

## Security

Do not commit `.arango`, `.env`, endpoints of private deployments, or credentials. CI scans the full git history for secrets with gitleaks. Report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Released under the [MIT License](LICENSE).
