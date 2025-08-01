# ArangoDB Cluster Management Guide

This guide covers how to configure and manage multiple ArangoDB clusters for the AWS Ontology transformation project.

## 📋 Overview

The AWS Ontology ArangoDB integration supports multiple cluster configurations through a centralized `.arango` configuration file. This allows you to:

- **Manage multiple environments** (development, staging, production)
- **Switch between local Docker and cloud instances** seamlessly
- **Automatically handle Docker container lifecycle**
- **Secure credential management** without committing secrets

## 🔧 Configuration File Format

Create a `.arango` file in your project root with the following structure:

```yaml
# ArangoDB Connection Configurations
# This file contains sensitive credentials - never commit to repository

clusters:
  # Local Docker cluster
  local_dev:
    type: "docker"
    name: "Local Development"
    container_name: "arango-dev"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "development_password"
    
  # Cloud production cluster
  production:
    type: "cloud"
    name: "Production Environment"
    endpoint: "https://your-prod-server.arangodb.cloud:8529"
    username: "prod_user"
    password: "secure_production_password"
    
  # Cloud staging cluster
  staging:
    type: "cloud"
    name: "Staging Environment"
    endpoint: "https://your-staging-server.arangodb.cloud:8529"
    username: "stage_user"
    password: "staging_password"

# Default cluster to use when none specified
default: "local_dev"
```

## 🏗️ Cluster Types

### Docker Clusters (`type: "docker"`)

For local development environments running ArangoDB in Docker containers.

**Required fields:**
- `type: "docker"`
- `name`: Human-readable description
- `container_name`: Docker container name
- `endpoint`: Usually `http://localhost:8529`
- `username`: ArangoDB username
- `password`: ArangoDB password

**Features:**
- ✅ Automatic container status detection
- ✅ Automatic container startup when needed
- ✅ Container lifecycle management
- ✅ Health checks before operations

### Cloud Clusters (`type: "cloud"`)

For ArangoDB Cloud instances or remote servers.

**Required fields:**
- `type: "cloud"`
- `name`: Human-readable description  
- `endpoint`: Full HTTPS URL to your cloud instance
- `username`: Cloud instance username
- `password`: Cloud instance password

**Features:**
- ✅ SSL/TLS encryption (auto-detected from https:// URLs)
- ✅ Connection parameter validation
- ✅ Cloud-specific error handling

## 🛠️ Cluster Operations

### List All Clusters

```bash
# Show all clusters with status
python tools/transform_ontology.py --list-clusters

# Alternative using demo tool
python tools/demo_cluster_management.py --list-clusters
```

**Example output:**
```
🗂️  Available ArangoDB Clusters:
==================================================
  📊 local_dev            | Local Development         | docker   🔴 Stopped ⭐ Default
     http://localhost:8529
  📊 staging              | Staging Environment       | cloud   
     https://staging.arangodb.cloud:8529
  📊 production           | Production Environment    | cloud   
     https://prod.arangodb.cloud:8529
```

### Test Connection

```bash
# Test specific cluster
python tools/transform_ontology.py --cluster production --test-connection

# Test with detailed output
python tools/demo_cluster_management.py --cluster staging --test-connection
```

### Docker Container Management

```bash
# Start container manually
python tools/transform_ontology.py --cluster local_dev --start-container

# Check container status
python tools/demo_cluster_management.py --cluster local_dev --test-connection
```

**The system automatically:**
- ✅ Detects container status (running/stopped/not found)
- ✅ Starts stopped containers when needed
- ✅ Shows helpful error messages for missing containers
- ✅ Waits for containers to be ready after startup

## 🚀 Using Clusters for Transformations

### Default Cluster

```bash
# Uses cluster specified in "default" field
python tools/transform_ontology.py --patterns pgt
```

### Specific Cluster

```bash
# Use local development cluster
python tools/transform_ontology.py --cluster local_dev --patterns pgt

# Use production cluster with multiple patterns
python tools/transform_ontology.py --cluster production --patterns pgt lpgt
```

### Environment-Specific Workflows

```bash
# Development workflow
python tools/transform_ontology.py --cluster local_dev --test-connection
python tools/transform_ontology.py --cluster local_dev --patterns pgt

# Staging deployment
python tools/transform_ontology.py --cluster staging --test-connection
python tools/transform_ontology.py --cluster staging --patterns pgt lpgt

# Production deployment
python tools/transform_ontology.py --cluster production --test-connection
python tools/transform_ontology.py --cluster production --patterns pgt
```

## 🔒 Security Best Practices

### Configuration File Security

- ✅ **Never commit `.arango` to git** - it's automatically in `.gitignore`
- ✅ **Use strong passwords** for all clusters
- ✅ **Rotate passwords regularly** especially for production
- ✅ **Limit access** to the `.arango` file on shared systems

### Password Management

```bash
# Passwords are always masked in output
🔗 Connection Parameters for 'production':
   Host: prod.arangodb.cloud:8529
   Username: prod_user
   Password: ********************  # Always masked
   Database: aws_ontology
   SSL: True
```

### Environment Separation

- Use different usernames/passwords for each environment
- Never use production credentials in development
- Test connections before running transformations
- Use least-privilege access principles

## 🎯 Configuration Examples

### Simple Local Setup

```yaml
clusters:
  local:
    type: "docker"
    name: "Local ArangoDB"
    container_name: "arango"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "password"

default: "local"
```

### Multi-Environment Setup

```yaml
clusters:
  # Development
  dev:
    type: "docker"
    name: "Development"
    container_name: "arango-dev"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "dev_pass"
    
  # Staging
  staging:
    type: "cloud"
    name: "Staging Cloud"
    endpoint: "https://abc123.arangodb.cloud:8529"
    username: "stage_user"
    password: "stage_secure_pass"
    
  # Production
  prod:
    type: "cloud"
    name: "Production Cloud"
    endpoint: "https://xyz789.arangodb.cloud:8529"
    username: "prod_user"
    password: "prod_very_secure_pass"

default: "dev"
```

### Project-Specific Clusters

```yaml
clusters:
  # ProjectA project
  project_a_local:
    type: "docker"
    name: "ProjectA Local"
    container_name: "project_a"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "project_a_pass"
    
  project_a_cloud:
    type: "cloud"
    name: "ProjectA Production"
    endpoint: "https://project_a.arangodb.cloud:8529"
    username: "project_a_user"
    password: "project_a_cloud_pass"
    
  # ProjectB project
  project_b_local:
    type: "docker"
    name: "ProjectB Local"
    container_name: "project_b"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "project_b_pass"

default: "project_a_local"
```

## 🆘 Troubleshooting

### Common Issues

**1. Container won't start**
```bash
# Check if container exists
docker ps -a | grep your_container_name

# Check container logs
docker logs your_container_name

# Recreate container if needed
docker rm your_container_name
docker run -d --name your_container_name -p 8529:8529 arangodb/arangodb
```

**2. Connection timeout to cloud cluster**
```bash
# Test network connectivity
ping your-server.arangodb.cloud

# Verify credentials
python tools/demo_cluster_management.py --cluster your_cluster --test-connection
```

**3. Default cluster not found**
```bash
# Check cluster names
python tools/transform_ontology.py --list-clusters

# Update default in .arango file
default: "correct_cluster_name"
```

### Debug Mode

For detailed debugging, examine connection parameters:

```bash
python tools/demo_cluster_management.py --cluster <name> --test-connection
```

This shows:
- Host and port details
- Username (password masked)
- SSL settings
- Container status (for Docker clusters)

## 📚 API Reference

### Command Line Options

| Option | Description |
|--------|-------------|
| `--list-clusters` | Show all configured clusters |
| `--cluster <name>` | Specify cluster to use |
| `--test-connection` | Test connectivity |
| `--start-container` | Start Docker container |
| `--config <path>` | Path to config file (default: .arango) |

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | "docker" or "cloud" |
| `name` | Yes | Human-readable name |
| `endpoint` | Yes | Full URL to ArangoDB |
| `username` | Yes | Database username |
| `password` | Yes | Database password |
| `container_name` | Docker only | Docker container name |
| `default` | Root level | Default cluster name |

## 🔄 Migration Guide

### From Direct Connection Parameters

**Old way:**
```bash
python tools/transform_ontology.py --host localhost --port 8529 --username root --password secret
```

**New way:**
1. Add to `.arango`:
```yaml
clusters:
  local:
    type: "docker"
    name: "Local"
    container_name: "arango"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "secret"
default: "local"
```

2. Use cluster:
```bash
python tools/transform_ontology.py --cluster local
```

**Note:** Legacy parameters still work but are deprecated.

For more examples, run: `python tools/quick_start.py`