# AWS Ontology ArangoDB Integration

This private repository contains tools and utilities for transforming the [AWS Ontology](https://github.com/ArthurKeen/AWS_Ontology) into ArangoDB graph databases for advanced querying and analysis.

## 🚀 Quick Start

```bash
# Clone this repository
git clone <private-repo-url>
cd aws-ontology-arango

# Install dependencies
pip install -r requirements.txt

# Transform the ontology
python tools/transform_ontology.py --pattern pgt --include-examples
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

## 🚀 Usage Examples

```bash
# Transform with PGT pattern (recommended)
python tools/transform_ontology.py --pattern pgt --include-examples

# Custom database and connection
python tools/transform_ontology.py \
    --pattern lpgt \
    --host my-server \
    --database my_aws_db \
    --include-examples
```

## 📞 Support

For issues and questions, contact the maintainer for access and support.

---

**Note**: This repository contains proprietary analysis tools and is maintained separately from the public AWS Ontology project.
