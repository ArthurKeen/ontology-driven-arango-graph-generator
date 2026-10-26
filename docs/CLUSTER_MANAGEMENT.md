# ArangoDB Cluster Management Guide

The tools read connection profiles ("clusters") from a local `.arango` YAML file. This file can contain credentials, so it is git-ignored and must never be committed.

## Create Local Configuration

```bash
cp .arango.example .arango
```

Edit `.arango` for your environment:

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
    password_env: "ARANGO_CLOUD_DEMO_PASSWORD"
    database: "graph_ontology"

default: "local_dev"
```

## Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `endpoint` | yes | | ArangoDB URL; `https://` enables TLS |
| `type` | no | | `docker` for a local container; anything else (e.g. `cloud`) for a remote server |
| `container_name` | for `docker` | | Exact Docker container name |
| `name` | no | cluster ID | Display name |
| `username` | no | `root` | ArangoDB user |
| `password` | no | empty | Password stored in the file |
| `password_env` | no | | Name of an environment variable holding the password; takes precedence over `password` |
| `database` | no | `graph_ontology` | Target database; created if missing and the user may create databases |

`default` selects the cluster used when `--cluster` is omitted. If `default` is not set, the first cluster is used. If it names a cluster that doesn't exist, the file is rejected.

The configuration is validated when it is loaded. Missing endpoints, Docker clusters without `container_name`, and unknown defaults are reported immediately.

## Keeping Passwords Out of the File

Use `password_env` for shared or remote deployments:

```bash
export ARANGO_CLOUD_DEMO_PASSWORD='...'
ontology-transform --cluster cloud_demo --test-connection
```

For one-off connections without a `.arango` file, use `--endpoint` and set `ARANGO_PASSWORD`. Passwords are never accepted as command-line flags, so they cannot end up in shell history or process listings.

```bash
export ARANGO_PASSWORD='...'
ontology-transform --endpoint https://example.arangodb.cloud:8529 --username demo_user --test-connection
```

## Common Commands

```bash
# Start local ArangoDB from this repository (ARANGO_PORT and ARANGO_ROOT_PASSWORD are optional)
docker compose up -d

# List configured clusters with Docker status
ontology-transform --list-clusters

# Show masked connection details and test the connection
ontology-transform --cluster local_dev --test-connection

# Start the Docker container configured for a cluster
ontology-transform --cluster local_dev --start-container

# Use a different database than the one configured
ontology-transform --cluster local_dev --database other_ontology --owl examples/ontology.owl
```

Commands that connect to a Docker cluster start a stopped container automatically and wait until ArangoDB responds.

## Database Permissions

The tool connects to the target database first. A user that has access to an existing database does not need `_system` access. Creating a missing database requires a user that is allowed to create databases.

## Security Practices

- Keep `.arango` local and ignored.
- Prefer `password_env` over `password` for anything other than local development.
- Use separate, least-privilege users for development and production.
- Rotate any credential that was ever committed or shared in logs.

## Troubleshooting

| Message | Fix |
|---------|-----|
| `Configuration file .arango not found` | `cp .arango.example .arango`, or use `--endpoint` |
| `Cluster 'x' not found` | Check names with `ontology-transform --list-clusters` |
| `Docker container 'x' not found` | Create it with `docker compose up -d` |
| `Docker is not installed or the Docker daemon is not running` | Start Docker Desktop |
| `Not authorized for database ...` | Check the password, and that the database exists and the user can access it |
| `... reads its password from $VAR, which is not set` | Export the variable named in `password_env` |

Run `ontology-env` to check Python, dependencies, Docker, and your `.arango` file in one go.
