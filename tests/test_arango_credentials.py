from pathlib import Path

import pytest

from tools.arango_credentials import ArangoCredentialManager


def write_config(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_cluster_and_connection_params(tmp_path):
    config_path = write_config(
        tmp_path / ".arango",
        """
clusters:
  local_dev:
    type: "docker"
    name: "Local Development"
    container_name: "ontology-arango"
    endpoint: "http://localhost:8529"
    username: "root"
    password: "change-me"
    database: "graph_ontology"
default: "local_dev"
""",
    )

    manager = ArangoCredentialManager(str(config_path))

    assert manager.get_default_cluster() == "local_dev"
    assert manager.list_clusters() == [
        {
            "id": "local_dev",
            "name": "Local Development",
            "type": "docker",
            "endpoint": "http://localhost:8529",
        }
    ]
    assert manager.get_connection_params("local_dev") == {
        "host": "localhost",
        "port": 8529,
        "username": "root",
        "password": "change-me",
        "database": "graph_ontology",
        "use_ssl": False,
    }


def test_default_falls_back_to_first_cluster(tmp_path):
    config_path = write_config(
        tmp_path / ".arango",
        """
clusters:
  first:
    endpoint: "https://example.arangodb.cloud:8529"
""",
    )

    manager = ArangoCredentialManager(str(config_path))

    assert manager.get_default_cluster() == "first"


def test_rejects_missing_clusters_section(tmp_path):
    config_path = write_config(tmp_path / ".arango", "default: local_dev\n")

    with pytest.raises(ValueError, match="missing 'clusters'"):
        ArangoCredentialManager(str(config_path))
