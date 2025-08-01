# Ontology-Driven ArangoDB Graph Generator

This repository contains tools and utilities for transforming **any ontology** (OWL/RDF) and sample data into ArangoDB graph databases using multiple graph models (RDF, Property Graph, Labeled Property Graph) for advanced querying and analysis.

## 🚀 Quick Start

```bash
# Clone this repository
git clone <repo-url>
cd ontology-driven-arango-graph-generator

# Check environment and install dependencies
python tools/setup_environment.py --install-deps

# List available clusters
python tools/transform_ontology.py --list-clusters

# Test connection to a cluster
python tools/transform_ontology.py --cluster local_dev --test-connection

# Transform your ontology
python tools/transform_ontology.py --cluster local_dev --patterns pgt
```

## 📋 Overview

This repository provides a comprehensive **ontology-driven graph generation system** for ArangoDB, including:

- **Multiple Graph Models**: Transform ontologies into RDF, Property Graph (PG), or Labeled Property Graph (LPG) models
- **Universal Ontology Support**: Works with any OWL/RDF ontology and sample data
- **Production-Ready Tools**: Robust transformation scripts with error handling
- **Advanced Query Capabilities**: AQL queries optimized for different graph models
- **Performance Optimization**: Indexing strategies and query optimization for each model
- **Automation Support**: Batch processing and CI/CD integration

## 🔄 Transformation Patterns

### RPT (RDF Preserving Transformation)
- **Creates**: RDF graph model preserving complete ontology semantics
- **Best for**: Semantic reasoning, SPARQL queries, research applications
- **Performance**: Full semantic preservation with RDFS/OWL inference support

### PGT (Property Graph Transformation) 
- **Creates**: Property graph with optimized vertex/edge collections
- **Best for**: High-performance graph traversal, production applications
- **Performance**: Fastest queries, minimal storage, optimized for AQL

### LPGT (Labeled Property Graph Transformation)
- **Creates**: Labeled property graph with rich schema information
- **Best for**: Complex analytics, multi-model queries, data integration
- **Performance**: Balanced semantics and performance with flexible labeling

## 🔧 Cluster Management

The system uses a `.arango` configuration file to manage multiple ArangoDB instances:

```bash
# List all configured clusters
python tools/transform_ontology.py --list-clusters

# Test connection to a specific cluster
python tools/transform_ontology.py --cluster local_dev --test-connection

# Start Docker container for local clusters
python tools/transform_ontology.py --cluster local_dev --start-container

# Check environment and install dependencies
python tools/setup_environment.py --install-deps
```

### Cluster Configuration

Create a `.arango` file in the project root:

```yaml
clusters:
  local_dev:
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

default: "local_dev"
```

## 🚀 Usage Examples

```bash
# Transform with PGT pattern using default cluster
python tools/transform_ontology.py --patterns pgt

# Transform using specific cluster  
python tools/transform_ontology.py --cluster production --patterns pgt

# Multiple transformation patterns
python tools/transform_ontology.py --cluster local_dev --patterns pgt lpgt

# Transform with custom ontology files
python tools/transform_ontology.py --cluster local_dev --patterns pgt \
    --owl /path/to/your/ontology.owl --ttl /path/to/your/sample_data.ttl

# Legacy mode (still supported)
python tools/transform_ontology.py \
    --host my-server \
    --database my_graph_db \
    --patterns pgt
```

## 📚 Documentation

### Complete Documentation Available

- **[📖 Documentation Index](docs/README.md)** - Complete documentation overview and navigation guide
- **[🔧 Cluster Management Guide](docs/CLUSTER_MANAGEMENT.md)** - Comprehensive cluster setup and management
- **[📋 API Reference](docs/API_REFERENCE.md)** - Complete command and programming reference
- **[📁 Project Structure](docs/PROJECT_STRUCTURE.md)** - Repository organization and architecture
- **[🛠️ Tools Documentation](tools/README.md)** - Detailed tool usage and examples

### Quick References

```bash
# Interactive demonstration of all features
python tools/quick_start.py

# Environment setup and validation
python tools/setup_environment.py --install-deps

# Help with any tool
python tools/transform_ontology.py --help
```

## 🔒 Security

- **Credential files (`.arango`) are automatically git-ignored**
- **Passwords are masked in all output displays**
- **Never commit sensitive configuration to the repository**
- **Use separate credentials for each environment**

## 📞 Support

For issues and questions:
1. **Check the documentation**: Start with [📖 Documentation Index](docs/README.md)
2. **Run diagnostics**: `python tools/setup_environment.py`
3. **Try the demo**: `python tools/quick_start.py`
4. **Contact maintainer** for access and advanced support

---

**Note**: This repository provides a general-purpose ontology transformation system with enterprise-grade cluster management capabilities for any ontology and graph model requirements.
