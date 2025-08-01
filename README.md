# AWS Ontology ArangoDB Integration

This private repository contains tools and utilities for transforming the [AWS Ontology](https://github.com/ArthurKeen/AWS_Ontology) into ArangoDB graph databases for advanced querying and analysis.

## 🚀 Quick Start

```bash
# Clone this repository
git clone <private-repo-url>
cd aws-ontology-arango

# Check environment and install dependencies
python tools/setup_environment.py --install-deps

# List available clusters
python tools/transform_ontology.py --list-clusters

# Test connection to a cluster
python tools/transform_ontology.py --cluster project_a_local --test-connection

# Transform the ontology
python tools/transform_ontology.py --cluster project_a_local --patterns pgt
```

## 📋 Overview

This repository provides ArangoDB integration capabilities for the AWS Ontology project, including:

- **Multiple Transformation Patterns**: RPT, PGT, and LPGT for different use cases
- **Production-Ready Tools**: Robust transformation scripts with error handling
- **Advanced Query Examples**: AQL queries for common AWS analysis scenarios
- **Performance Optimization**: Indexing strategies and query optimization
- **Automation Support**: Batch processing and CI/CD integration

## 🔄 Transformation Patterns

### RPT (RDF Preserving Transformation)
- **Best for**: Complex reasoning, research, schema flexibility
- **Performance**: Full semantic preservation

### PGT (Property Graph Transformation) 
- **Best for**: Production applications, balanced needs
- **Performance**: Fastest queries, minimal storage 

### LPGT (Labeled Property Graph Transformation)
- **Best for**: Production applications, schema flexibility
- **Performance**: fast performance, reduced storage

## 🔧 Cluster Management

The system uses a `.arango` configuration file to manage multiple ArangoDB instances:

```bash
# List all configured clusters
python tools/transform_ontology.py --list-clusters

# Test connection to a specific cluster
python tools/transform_ontology.py --cluster project_a_local --test-connection

# Start Docker container for local clusters
python tools/transform_ontology.py --cluster project_a_local --start-container

# Check environment and install dependencies
python tools/setup_environment.py --install-deps
```

### Cluster Configuration

Create a `.arango` file in the project root:

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

## 🚀 Usage Examples

```bash
# Transform with PGT pattern using default cluster
python tools/transform_ontology.py --patterns pgt

# Transform using specific cluster
python tools/transform_ontology.py --cluster production --patterns pgt

# Multiple transformation patterns
python tools/transform_ontology.py --cluster local --patterns pgt lpgt

# Legacy mode (still supported)
python tools/transform_ontology.py \
    --host my-server \
    --database my_aws_db \
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

**Note**: This repository contains proprietary analysis tools with enterprise-grade cluster management capabilities, maintained separately from the public AWS Ontology project.
