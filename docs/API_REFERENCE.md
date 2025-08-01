# API Reference - AWS Ontology ArangoDB Integration

Complete reference for all tools, command-line options, and configuration formats.

## 🛠️ Command Line Tools

### `transform_ontology.py` - Main Transformation Tool

**Description:** Primary tool for transforming AWS Ontology into ArangoDB using cluster-based authentication.

#### Cluster Management Commands

```bash
python tools/transform_ontology.py [OPTIONS]
```

| Option | Type | Description |
|--------|------|-------------|
| `--list-clusters` | flag | List all available clusters with status |
| `--cluster <name>` | string | Specify cluster to use from .arango file |
| `--test-connection` | flag | Test connection to specified cluster |
| `--start-container` | flag | Start Docker container for cluster |
| `--setup-deps` | flag | Install missing Python dependencies |
| `--config <path>` | string | Path to config file (default: .arango) |

#### Transformation Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--patterns <list>` | list | `["pgt"]` | Transformation patterns to apply |
| `--owl <path>` | string | `"ontology/aws.owl"` | Path to OWL ontology file |
| `--ttl <path>` | string | `"ontology/examples.ttl"` | Path to TTL examples file |

#### Legacy Connection Options (deprecated)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | string | `"localhost"` | ArangoDB host |
| `--port` | integer | `8529` | ArangoDB port |
| `--username` | string | `"root"` | ArangoDB username |
| `--password` | string | `""` | ArangoDB password |
| `--database` | string | `"aws_ontology"` | Database name |

#### Transformation Patterns

| Pattern | Full Name | Best For | Performance |
|---------|-----------|----------|-------------|
| `rpt` | RDF Preserving Transformation | Complex reasoning, research | Full semantic preservation |
| `pgt` | Property Graph Transformation | Production applications | Fastest queries, minimal storage |
| `lpgt` | Labeled Property Graph Transformation | Production with schema flexibility | Fast performance, reduced storage |

#### Examples

```bash
# List clusters
python tools/transform_ontology.py --list-clusters

# Test connection
python tools/transform_ontology.py --cluster production --test-connection

# Transform with specific cluster
python tools/transform_ontology.py --cluster staging --patterns pgt lpgt

# Install dependencies
python tools/transform_ontology.py --setup-deps
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (missing dependencies, configuration, etc.) |

---

### `setup_environment.py` - Environment Setup

**Description:** Validates environment and installs missing dependencies.

```bash
python tools/setup_environment.py [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `--install-deps` | Attempt automatic dependency installation |

#### Validation Checks

- ✅ Python version (3.8+ required)
- ✅ Docker availability and daemon status
- ✅ Configuration file existence (.arango)
- ✅ Core dependencies (PyYAML, rdflib, python-arango)
- ✅ Optional dependencies (arangordf, owlready2)

#### Examples

```bash
# Check environment
python tools/setup_environment.py

# Install missing dependencies
python tools/setup_environment.py --install-deps
```

---

### `demo_cluster_management.py` - Cluster Management Demo

**Description:** Standalone tool for cluster management operations.

```bash
python tools/demo_cluster_management.py [OPTIONS]
```

#### Options

| Option | Type | Description |
|--------|------|-------------|
| `--list-clusters` | flag | List all available clusters |
| `--cluster <name>` | string | Specify cluster to operate on |
| `--test-connection` | flag | Test connection to cluster |
| `--start-container` | flag | Start Docker container |
| `--config <path>` | string | Path to config file |

#### Examples

```bash
# List clusters
python tools/demo_cluster_management.py --list-clusters

# Test connection
python tools/demo_cluster_management.py --cluster local --test-connection

# Start container
python tools/demo_cluster_management.py --cluster local --start-container
```

---

### `quick_start.py` - Complete Demonstration

**Description:** Comprehensive demonstration of all capabilities.

```bash
python tools/quick_start.py
```

**No options** - runs complete demonstration showing:
- Environment validation
- Cluster management
- Connection testing
- Container management
- Transformation examples

---

### `test_credentials.py` - Basic Testing

**Description:** Simple test script for credential manager functionality.

```bash
python tools/test_credentials.py
```

**No options** - performs basic tests:
- Load configuration
- List clusters
- Test default cluster
- Check Docker status

## 📁 Configuration File Format

### `.arango` Configuration File

**Location:** Project root directory  
**Format:** YAML  
**Security:** Automatically added to `.gitignore`

#### Root Structure

```yaml
clusters:
  <cluster_name>:
    # Cluster configuration
    
default: "<cluster_name>"  # Optional default cluster
```

#### Cluster Configuration

##### Docker Clusters

```yaml
<cluster_name>:
  type: "docker"                    # Required: "docker"
  name: "<human_readable_name>"     # Required: Display name
  container_name: "<docker_name>"   # Required: Docker container name
  endpoint: "<url>"                 # Required: http://localhost:8529
  username: "<username>"            # Required: ArangoDB username
  password: "<password>"            # Required: ArangoDB password
```

##### Cloud Clusters

```yaml
<cluster_name>:
  type: "cloud"                     # Required: "cloud"
  name: "<human_readable_name>"     # Required: Display name
  endpoint: "<url>"                 # Required: https://server:8529
  username: "<username>"            # Required: Cloud username
  password: "<password>"            # Required: Cloud password
```

#### Configuration Validation

| Field | Docker | Cloud | Validation |
|-------|--------|-------|------------|
| `type` | ✅ | ✅ | Must be "docker" or "cloud" |
| `name` | ✅ | ✅ | Any descriptive string |
| `container_name` | ✅ | ❌ | Valid Docker container name |
| `endpoint` | ✅ | ✅ | Valid URL (http/https) |
| `username` | ✅ | ✅ | Non-empty string |
| `password` | ✅ | ✅ | Any string (can be empty) |

#### Example Configurations

**Minimal Configuration:**
```yaml
clusters:
  local:
    type: "docker"
    name: "Local Dev"
    container_name: "arango"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "password"

default: "local"
```

**Multi-Environment Configuration:**
```yaml
clusters:
  dev:
    type: "docker"
    name: "Development"
    container_name: "arango-dev"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "dev_password"
    
  staging:
    type: "cloud"
    name: "Staging Environment"
    endpoint: "https://staging.arangodb.cloud:8529"
    username: "stage_user"
    password: "staging_secure_password"
    
  production:
    type: "cloud"
    name: "Production Environment"
    endpoint: "https://prod.arangodb.cloud:8529"
    username: "prod_user"
    password: "production_very_secure_password"

default: "dev"
```

## 🔧 Python API

### `ArangoCredentialManager` Class

**Module:** `tools.arango_credentials`

```python
from tools.arango_credentials import ArangoCredentialManager

# Initialize
manager = ArangoCredentialManager(config_path=".arango")
```

#### Methods

##### `__init__(config_path: str = ".arango")`
Initialize credential manager with configuration file.

**Parameters:**
- `config_path`: Path to .arango configuration file

**Raises:**
- `FileNotFoundError`: Config file not found
- `ValueError`: Invalid YAML or missing clusters section

##### `list_clusters() -> List[Dict[str, str]]`
Get list of all available clusters.

**Returns:**
```python
[
    {
        'id': 'cluster_name',
        'name': 'Display Name',
        'type': 'docker|cloud',
        'endpoint': 'http://...'
    },
    ...
]
```

##### `get_cluster_config(cluster_id: str) -> Dict[str, Any]`
Get complete configuration for a specific cluster.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:** Complete cluster configuration dictionary

**Raises:**
- `KeyError`: Cluster not found

##### `get_connection_params(cluster_id: str) -> Dict[str, Any]`
Get ArangoDB connection parameters for a cluster.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:**
```python
{
    'host': 'hostname',
    'port': 8529,
    'username': 'username',
    'password': 'password',
    'database': 'aws_ontology',
    'use_ssl': True|False
}
```

##### `get_default_cluster() -> str`
Get the default cluster ID.

**Returns:** Default cluster ID string

**Raises:**
- `ValueError`: No clusters configured or default not found

##### `is_docker_cluster(cluster_id: str) -> bool`
Check if cluster is Docker-based.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:** True if Docker cluster, False otherwise

##### `get_container_name(cluster_id: str) -> Optional[str]`
Get Docker container name for cluster.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:** Container name or None if not Docker cluster

##### `check_docker_container_status(cluster_id: str) -> Optional[str]`
Check Docker container status.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:** 
- `"running"`: Container is running
- `"stopped"`: Container exists but stopped
- `"not_found"`: Container doesn't exist
- `None`: Not a Docker cluster

##### `start_docker_container(cluster_id: str) -> bool`
Start Docker container for cluster.

**Parameters:**
- `cluster_id`: Cluster identifier

**Returns:** True if successful, False otherwise

##### `print_cluster_summary() -> None`
Print formatted summary of all clusters with status.

**Output:** Formatted table showing clusters, types, and status

### `AWSOntologyTransformer` Class

**Module:** `tools.transform_ontology`

```python
from tools.transform_ontology import AWSOntologyTransformer
from tools.arango_credentials import ArangoCredentialManager

# Cluster-based initialization
manager = ArangoCredentialManager()
transformer = AWSOntologyTransformer("cluster_id", manager)

# Legacy initialization
transformer = AWSOntologyTransformer(
    host="localhost", port=8529, username="root", 
    password="password", database="aws_ontology"
)
```

#### Methods

##### `__init__(cluster_id, credential_manager, **legacy_params)`
Initialize transformer with cluster or legacy parameters.

**Cluster Parameters:**
- `cluster_id`: Cluster identifier from .arango
- `credential_manager`: ArangoCredentialManager instance

**Legacy Parameters:**
- `host`, `port`, `username`, `password`, `database`

##### `load_ontology(owl_file: str, ttl_file: Optional[str] = None) -> Graph`
Load ontology from OWL and optional TTL files.

**Parameters:**
- `owl_file`: Path to OWL ontology file
- `ttl_file`: Optional path to TTL examples file

**Returns:** RDFlib Graph containing loaded ontology

##### `transform_rpt(graph: Graph, prefix: str = "rpt") -> None`
Apply RDF Preserving Transformation.

##### `transform_pgt(graph: Graph, prefix: str = "pgt") -> None`
Apply Property Graph Transformation.

##### `transform_lpgt(graph: Graph, prefix: str = "lpgt") -> None`
Apply Labeled Property Graph Transformation.

## 📦 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyYAML | >= 6.0 | Configuration file parsing |
| rdflib | >= 6.0.0 | RDF graph processing |
| python-arango | >= 7.5.0 | ArangoDB client library |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| arangordf | >= 0.1.0 | RDF to ArangoDB transformation |
| owlready2 | >= 0.45 | OWL ontology support |

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific packages
pip install PyYAML>=6.0 rdflib>=6.0.0 python-arango>=7.5.0
pip install arangordf>=0.1.0 owlready2>=0.45
```

## 🔍 Error Codes and Messages

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration file .arango not found` | Missing config file | Create .arango file in project root |
| `Cluster 'name' not found` | Invalid cluster name | Check `--list-clusters` for valid names |
| `arangordf library is required` | Missing transformation engine | Run `--setup-deps` or install manually |
| `Docker container 'name' not found` | Container doesn't exist | Create Docker container with specified name |
| `Failed to start container 'name'` | Docker daemon issue | Check Docker is running and container exists |

### Docker Container Status Messages

| Status | Icon | Meaning |
|--------|------|---------|
| Running | 🟢 | Container is active and ready |
| Stopped | 🔴 | Container exists but not running |
| Not Found | ❓ | Container doesn't exist |

### SSL Detection

| Endpoint Pattern | SSL Setting |
|------------------|-------------|
| `http://...` | `use_ssl: False` |
| `https://...` | `use_ssl: True` |

## 🎯 Usage Patterns

### Environment Workflow

```bash
# 1. Setup
python tools/setup_environment.py --install-deps

# 2. Explore
python tools/transform_ontology.py --list-clusters

# 3. Test
python tools/transform_ontology.py --cluster <name> --test-connection

# 4. Transform
python tools/transform_ontology.py --cluster <name> --patterns pgt
```

### Development Workflow

```bash
# Local development
python tools/transform_ontology.py --cluster local_dev --patterns pgt

# Staging validation
python tools/transform_ontology.py --cluster staging --patterns pgt lpgt

# Production deployment
python tools/transform_ontology.py --cluster production --patterns pgt
```

### Troubleshooting Workflow

```bash
# Check environment
python tools/setup_environment.py

# Test specific cluster
python tools/demo_cluster_management.py --cluster <name> --test-connection

# Start container if needed
python tools/transform_ontology.py --cluster <name> --start-container

# Retry transformation
python tools/transform_ontology.py --cluster <name> --patterns pgt
```

---

For interactive examples: `python tools/quick_start.py`  
For detailed cluster management: See [CLUSTER_MANAGEMENT.md](CLUSTER_MANAGEMENT.md)