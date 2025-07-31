# ArangoDB Transformation Tools

## Main Tool: `transform_ontology.py`

Converts the AWS Ontology into ArangoDB using three transformation patterns.

### Basic Usage

```bash
# Transform using PGT pattern (recommended)
python tools/transform_ontology.py --pattern pgt --include-examples

# Transform using RPT pattern (simple)
python tools/transform_ontology.py --pattern rpt

# Transform using LPGT pattern (full semantics)
python tools/transform_ontology.py --pattern lpgt --include-examples
```

### Parameters

- `--pattern`: Transformation pattern (rpt/pgt/lpgt) - Required
- `--ontology-path`: Path to ontology file (default: `../AWS_Ontology/ontology/aws.ttl`)
- `--include-examples`: Include example instances
- `--host`: ArangoDB host (default: localhost)
- `--port`: ArangoDB port (default: 8529)
- `--database`: Target database name (default: aws_ontology)

### Transformation Patterns

- **RPT**: Simple graph structure, fastest queries
- **PGT**: Balanced features and performance (recommended)
- **LPGT**: Full RDF semantics, complex reasoning

## Requirements

- ArangoDB 3.8+ running
- Python dependencies: `pip install -r requirements.txt`
- AWS Ontology repository available at `../AWS_Ontology/`
