# ArangoDB Cluster Management Guide

The tools use a local `.arango` YAML file to manage one or more ArangoDB targets. This file can contain credentials, so it is ignored by git and must never be committed.

## Create Local Configuration

```bash
cp .arango.example .arango
```

Edit `.arango` for your local environment:

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
    name: "Cloud Demo"
    endpoint: "https://example.arangodb.cloud:8529"
    username: "demo_user"
    password: "replace-with-your-secret"
    database: "graph_ontology"

default: "local_dev"
```

## Cluster Types

### Docker Clusters

Docker clusters represent local ArangoDB containers. Required fields:

- `type`: `docker`
- `name`: display name
- `container_name`: Docker container name
- `endpoint`: usually `http://localhost:8529`
- `username`: ArangoDB username
- `password`: ArangoDB password
- `database`: target database name

### Cloud Clusters

Cloud clusters represent ArangoDB Cloud or another remote ArangoDB server. Required fields:

- `type`: `cloud`
- `name`: display name
- `endpoint`: HTTPS endpoint
- `username`: ArangoDB username
- `password`: ArangoDB password
- `database`: target database name

## Common Commands

```bash
# Start local ArangoDB from this repository
docker compose up -d

# List configured clusters
python tools/transform_ontology.py --list-clusters

# Test one cluster
python tools/transform_ontology.py --cluster local_dev --test-connection

# Start the Docker container configured for a cluster
python tools/transform_ontology.py --cluster local_dev --start-container

# Inspect connection parameters with password masking
python tools/demo_cluster_management.py --cluster local_dev --test-connection
```

## Transform With a Cluster

```bash
python tools/transform_ontology.py --cluster local_dev --patterns pgt \
  --owl /path/to/ontology.owl \
  --ttl /path/to/sample_data.ttl
```

## Security Practices

- Keep `.arango` local and ignored.
- Use placeholders in examples and documentation.
- Rotate credentials that were ever committed or shared in logs.
- Use separate credentials for development, staging, and production.
- Prefer least-privilege database users for transformations.

## Troubleshooting

### Missing `.arango`

```bash
cp .arango.example .arango
python tools/setup_environment.py
```

### Docker Container Not Found

```bash
docker compose up -d
python tools/transform_ontology.py --cluster local_dev --test-connection
```

### Cloud Connection Fails

Check the endpoint, username, password, and network access. Use the demo tool to inspect non-secret connection parameters:

```bash
python tools/demo_cluster_management.py --cluster cloud_demo --test-connection
```

## Migration From Direct Parameters

Legacy direct parameters still work, but `.arango` is preferred.

Old style:

```bash
python tools/transform_ontology.py --host localhost --port 8529 --username root --password <password>
```

Preferred style:

```bash
python tools/transform_ontology.py --cluster local_dev --patterns pgt
```
