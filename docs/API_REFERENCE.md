# API Reference

Reference for the command-line tools and the Python API.

## `ontology-transform`

Loads an ontology and applies one or more transformation patterns. You can also run it as `python -m ontology_graph_generator`.

```bash
ontology-transform [connection options] --owl FILE [transformation options]
```

### Connection Options

| Option | Default | Description |
|--------|---------|-------------|
| `--config <path>` | `.arango` | Cluster configuration file |
| `--list-clusters` | | List configured clusters with Docker status and exit |
| `--cluster <id>` | configured default | Cluster from the configuration file |
| `--endpoint <url>` | | Connect directly instead of using a cluster; password from `ARANGO_PASSWORD` |
| `--username <name>` | `root` | Username for `--endpoint` connections |
| `--database <name>` | cluster's `database`, else `graph_ontology` | Target database (created if missing) |
| `--test-connection` | | Show masked connection details, connect, and exit |
| `--start-container` | | Start the selected Docker cluster's container and exit |

`--endpoint` cannot be combined with `--cluster` or `--start-container`.

### Transformation Options

| Option | Default | Description |
|--------|---------|-------------|
| `--owl <path>` | required | Ontology file. The format is detected from the content and extension (RDF/XML, Turtle, JSON-LD, N-Triples) |
| `--ttl <path>` | | Optional instance data loaded into the same graph |
| `--rdf-format <fmt>` | detected | Force an rdflib format for both files, e.g. `xml` or `turtle` |
| `--patterns <p> ...` | `pgt` | Any of `rpt`, `pgt`, `lpgt` |
| `--graph-name <name>` | `ontology_graph` | Each pattern writes the graph `<pattern>_<name>` |
| `--overwrite` | off | Drop existing graphs and their collections first. Without it, re-runs update documents in place |
| `-v`, `--verbose` | off | Show detailed logs and full tracebacks |
| `--version` | | Print the version and exit |

Input files are loaded and validated before connecting to ArangoDB, so a mistyped path fails immediately.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime error (configuration, files, connection, transformation) |
| 2 | Invalid command-line arguments |

### Examples

```bash
ontology-transform --list-clusters
ontology-transform --cluster local_dev --test-connection
ontology-transform --cluster local_dev --owl examples/ontology.owl --ttl examples/sample_data.ttl
ontology-transform --cluster local_dev --owl my.owl --patterns pgt lpgt --graph-name my --overwrite
ontology-transform --endpoint http://localhost:8529 --database scratch --owl my.ttl --patterns rpt
```

## `ontology-env`

Checks the Python version, required packages, Docker, and the `.arango` file. Docker and a missing `.arango` file only produce warnings. The command exits with code 1 if any required check fails.

```bash
ontology-env [--config PATH]
```

## Python API

```python
from ontology_graph_generator import (
    ArangoCredentialManager,
    OntologyGraphTransformer,
    load_ontology,
)

graph = load_ontology("examples/ontology.owl", "examples/sample_data.ttl")

# From a configured cluster
manager = ArangoCredentialManager(".arango")
transformer = OntologyGraphTransformer.from_cluster(manager, "local_dev")

# Or directly
transformer = OntologyGraphTransformer.connect(
    endpoint="http://localhost:8529",
    username="root",
    password="change-me",
    database="graph_ontology",
)

transformer.transform(graph, "pgt", graph_name="pgt_org", overwrite=True)
```

### `load_ontology(owl_file, ttl_file=None, rdf_format=None) -> rdflib.Graph`

Parses the ontology and optional data file into one graph. Raises `FileNotFoundError` for missing files and `ValueError` for files that cannot be parsed.

### `OntologyGraphTransformer`

| Member | Description |
|--------|-------------|
| `OntologyGraphTransformer(db)` | Wrap an existing `python-arango` database |
| `connect(endpoint, username, password, database, create_database=True)` | Connect, creating the database if missing. Raises `PermissionError` on authorization failures |
| `from_cluster(manager, cluster_id, database=None)` | Connect using a configured cluster |
| `transform(graph, pattern, graph_name=None, overwrite=False)` | Apply `rpt`, `pgt` or `lpgt`; returns the `python-arango` graph |
| `db` | The connected `python-arango` database |

`PATTERNS` maps each pattern name to its description and the arango-rdf method it calls.

### `ArangoCredentialManager`

| Method | Description |
|--------|-------------|
| `ArangoCredentialManager(config_path=".arango")` | Load and validate the configuration. Raises `FileNotFoundError` or `ValueError` |
| `list_clusters()` | `[{"id", "name", "type", "endpoint"}, ...]` |
| `get_cluster_config(cluster_id)` | Raw cluster settings. Raises `KeyError` for unknown clusters |
| `get_connection_params(cluster_id)` | `{"endpoint", "host", "port", "username", "password", "database", "use_ssl"}`, with `password_env` resolved |
| `get_default_cluster()` | `default`, or the first cluster |
| `is_docker_cluster(cluster_id)` / `get_container_name(cluster_id)` | Docker cluster details |
| `check_docker_container_status(cluster_id)` | `"running"`, `"stopped"`, `"not_found"`, `"docker_unavailable"`, or `None` for non-Docker clusters |
| `start_docker_container(cluster_id)` | Start the container; returns `True` on success |
| `print_cluster_summary()` | Print the cluster table used by `--list-clusters` |

Helper functions in `ontology_graph_generator.arango_credentials`:

- `mask_secret(secret)` returns a fixed-width mask that reveals neither the value nor its length.
- `wait_for_endpoint(endpoint, timeout=60)` waits until an ArangoDB server responds.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| arango-rdf | >= 2.0.0 | RDF to ArangoDB transformations |
| python-arango | >= 8.0.0 | ArangoDB client |
| rdflib | >= 6.0.0 | RDF parsing |
| PyYAML | >= 6.0 | Configuration parsing |

All dependencies are declared in `pyproject.toml`.
