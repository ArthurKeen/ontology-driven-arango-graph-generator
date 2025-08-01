# ArangoDB Transformation Tools

This directory contains tools for transforming the AWS Ontology into ArangoDB using cluster-based credential management.

## 🚀 Quick Start

```bash
# Check environment and install dependencies
python tools/setup_environment.py --install-deps

# List available clusters
python tools/transform_ontology.py --list-clusters

# Test connection to a cluster
python tools/transform_ontology.py --cluster project_a_local --test-connection

# Transform the ontology
python tools/transform_ontology.py --cluster project_a_local --patterns pgt
```

## 🛠️ Main Tools

### `transform_ontology.py` - Main Transformation Tool
Converts the AWS Ontology into ArangoDB using cluster-based authentication and three transformation patterns.

**Cluster Management Commands:**
```bash
# List all configured clusters with status
python tools/transform_ontology.py --list-clusters

# Test connection to specific cluster
python tools/transform_ontology.py --cluster <cluster_name> --test-connection

# Start Docker container for local clusters
python tools/transform_ontology.py --cluster <cluster_name> --start-container

# Install missing dependencies
python tools/transform_ontology.py --setup-deps
```

**Transformation Commands:**
```bash
# Transform using PGT pattern (recommended)
python tools/transform_ontology.py --cluster project_a_local --patterns pgt

# Transform using multiple patterns
python tools/transform_ontology.py --cluster project_a_cloud --patterns pgt lpgt

# Transform using default cluster
python tools/transform_ontology.py --patterns pgt
```

### `setup_environment.py` - Environment Setup
Validates your environment and installs missing dependencies.

```bash
# Check environment status
python tools/setup_environment.py

# Install missing dependencies automatically
python tools/setup_environment.py --install-deps
```

### `demo_cluster_management.py` - Cluster Management Demo
Standalone tool for cluster management operations.

```bash
# List clusters
python tools/demo_cluster_management.py --list-clusters

# Test connection
python tools/demo_cluster_management.py --cluster <name> --test-connection

# Start container
python tools/demo_cluster_management.py --cluster <name> --start-container
```

### `quick_start.py` - Complete Demonstration
Shows all capabilities in action.

```bash
python tools/quick_start.py
```

## 📋 Command Line Options

### Cluster Management
- `--list-clusters`: Show all available clusters with status
- `--cluster <name>`: Specify which cluster to use
- `--test-connection`: Test connectivity to specified cluster
- `--start-container`: Start Docker container for cluster
- `--setup-deps`: Install missing Python dependencies

### Transformation Options
- `--patterns <list>`: Transformation patterns to apply (default: pgt)
  - `rpt`: RDF Preserving Transformation (complex reasoning)
  - `pgt`: Property Graph Transformation (recommended)
  - `lpgt`: Labeled Property Graph Transformation (production)
- `--owl <path>`: Path to OWL ontology file
- `--ttl <path>`: Path to TTL examples file

### Legacy Options (deprecated)
- `--host`, `--port`, `--username`, `--password`, `--database`: Direct connection parameters

## 🔧 Transformation Patterns

### RPT (RDF Preserving Transformation)
- **Best for**: Complex reasoning, research, schema flexibility
- **Performance**: Full semantic preservation
- **Use case**: When you need complete RDF semantics

### PGT (Property Graph Transformation)
- **Best for**: Production applications, balanced needs
- **Performance**: Fastest queries, minimal storage
- **Use case**: Most common production scenarios (recommended)

### LPGT (Labeled Property Graph Transformation)
- **Best for**: Production applications, schema flexibility
- **Performance**: Fast performance, reduced storage
- **Use case**: Production with complex labeling needs

## 📁 Configuration

### Cluster Configuration (`.arango` file)
Create a `.arango` file in the project root with your cluster configurations:

```yaml
clusters:
  local:
    type: "docker"
    name: "Local Development"
    container_name: "arango-dev"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "password"
    
  production:
    type: "cloud"
    name: "Production Cloud"
    endpoint: "https://your-server.arangodb.cloud:8529"
    username: "admin"
    password: "your_password"

default: "local"
```

## 🔒 Security

- The `.arango` file is automatically added to `.gitignore`
- Passwords are masked in all output displays
- Never commit credential files to the repository

## 📦 Requirements

- **Python 3.8+** 
- **Docker** (for local clusters)
- **Python Dependencies**: Automatically managed by setup tools
  - PyYAML >= 6.0 (configuration)
  - rdflib >= 6.0.0 (RDF processing)
  - python-arango >= 7.5.0 (ArangoDB client)
  - arangordf >= 0.1.0 (transformation engine)
  - owlready2 >= 0.45 (OWL support)

## 🎯 Examples

### Environment Setup
```bash
# Check what's missing
python tools/setup_environment.py

# Install everything
python tools/setup_environment.py --install-deps
```

### Cluster Operations
```bash
# See all clusters
python tools/transform_ontology.py --list-clusters

# Test before transforming
python tools/transform_ontology.py --cluster my_cluster --test-connection

# Start container if needed
python tools/transform_ontology.py --cluster my_cluster --start-container
```

### Transformations
```bash
# Quick transformation with default cluster
python tools/transform_ontology.py --patterns pgt

# Production transformation with specific cluster
python tools/transform_ontology.py --cluster production --patterns pgt lpgt

# Research transformation with local cluster
python tools/transform_ontology.py --cluster local --patterns rpt
```

## 🆘 Troubleshooting

### Missing Dependencies
```bash
python tools/transform_ontology.py --setup-deps
```

### Container Issues
```bash
# Check container status
python tools/transform_ontology.py --cluster <name> --test-connection

# Start container manually
python tools/transform_ontology.py --cluster <name> --start-container
```

### Connection Problems
```bash
# Test connectivity
python tools/transform_ontology.py --cluster <name> --test-connection

# Verify configuration
python tools/demo_cluster_management.py --cluster <name> --test-connection
```

For comprehensive examples, run: `python tools/quick_start.py`
