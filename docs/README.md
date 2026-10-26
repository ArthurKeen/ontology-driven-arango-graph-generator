# Documentation

| Document | Use it when |
|----------|-------------|
| [Main README](../README.md) | You are new to the project and want the quick start |
| [Cluster Management Guide](CLUSTER_MANAGEMENT.md) | You are setting up `.arango`, Docker, cloud deployments, or troubleshooting connections |
| [API Reference](API_REFERENCE.md) | You need every CLI option, exit codes, or the Python API |
| [Project Structure](PROJECT_STRUCTURE.md) | You are contributing and want to know where things live |
| [Release Checklist](RELEASE_CHECKLIST.md) | You are tagging a release |
| [Changelog](../CHANGELOG.md) | You want to know what changed between versions |

## Command Quick Reference

```bash
# Environment
ontology-env

# Clusters
ontology-transform --list-clusters
ontology-transform --cluster <name> --test-connection
ontology-transform --cluster <name> --start-container

# Transformations
ontology-transform --cluster <name> --owl examples/ontology.owl --ttl examples/sample_data.ttl
ontology-transform --cluster <name> --owl my.owl --patterns rpt pgt lpgt --overwrite
```

Tests check that every relative link in these documents resolves, and that every `ontology-transform` flag in the examples exists. A doc that drifts from the CLI therefore fails CI.
