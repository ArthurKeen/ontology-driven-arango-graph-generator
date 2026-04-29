# ArangoDB Transformation Tools

The `tools/` directory contains the command-line utilities for configuring ArangoDB clusters and transforming OWL/RDF input into graph models.

## Quick Start

```bash
python tools/setup_environment.py
python tools/transform_ontology.py --list-clusters
python tools/transform_ontology.py --cluster local_dev --test-connection
python tools/transform_ontology.py --cluster local_dev --patterns pgt \
  --owl /path/to/ontology.owl \
  --ttl /path/to/sample_data.ttl
```

## Main Tools

### `transform_ontology.py`

Main transformation CLI.

```bash
# List configured clusters
python tools/transform_ontology.py --list-clusters

# Test one cluster
python tools/transform_ontology.py --cluster local_dev --test-connection

# Start a Docker-backed cluster container
python tools/transform_ontology.py --cluster local_dev --start-container

# Run one or more transformation patterns
python tools/transform_ontology.py --cluster local_dev --patterns pgt lpgt
```

### `setup_environment.py`

Validates Python, Docker, local `.arango` configuration, and dependencies.

```bash
python tools/setup_environment.py
python tools/setup_environment.py --install-deps
```

### `demo_cluster_management.py`

Shows cluster connection parameters with password masking and Docker status.

```bash
python tools/demo_cluster_management.py --list-clusters
python tools/demo_cluster_management.py --cluster local_dev --test-connection
```

### `quick_start.py`

Runs an interactive tour of the setup and cluster commands.

```bash
python tools/quick_start.py
```

### `validate_documentation.py`

Runs documentation and repository sanity checks.

```bash
python tools/validate_documentation.py
```

## Transformation Patterns

- `rpt`: RDF Preserving Transformation.
- `pgt`: Property Graph Transformation.
- `lpgt`: Labeled Property Graph Transformation.

## Configuration

Create `.arango` from the safe example:

```bash
cp .arango.example .arango
```

Real credentials belong only in `.arango`, which is ignored by git.
