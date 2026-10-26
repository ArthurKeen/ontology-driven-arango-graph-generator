import subprocess
from pathlib import Path

import pytest

from ontology_graph_generator.arango_credentials import ArangoCredentialManager, mask_secret

LOCAL_DEV = """
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
"""


def write_config(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_cluster_and_connection_params(tmp_path):
    manager = ArangoCredentialManager(str(write_config(tmp_path / ".arango", LOCAL_DEV)))

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
        "endpoint": "http://localhost:8529",
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
  second:
    endpoint: "https://example2.arangodb.cloud:8529"
""",
    )

    manager = ArangoCredentialManager(str(config_path))

    assert manager.get_default_cluster() == "first"
    assert manager.get_connection_params("first")["use_ssl"] is True


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("default: local_dev\n", "missing 'clusters'"),
        ("clusters: {}\n", "non-empty mapping"),
        ("clusters:\n  a:\n    name: x\n", "needs an endpoint"),
        ("clusters:\n  a:\n    type: docker\n    endpoint: http://x\n", "needs a container_name"),
        ("clusters:\n  a:\n    endpoint: http://x\ndefault: b\n", "'b' is not defined"),
        ("clusters: [\n", "Invalid YAML"),
    ],
)
def test_rejects_invalid_configuration(tmp_path, content, message):
    config_path = write_config(tmp_path / ".arango", content)

    with pytest.raises(ValueError, match=message):
        ArangoCredentialManager(str(config_path))


def test_unknown_cluster_raises_key_error(tmp_path):
    manager = ArangoCredentialManager(str(write_config(tmp_path / ".arango", LOCAL_DEV)))

    with pytest.raises(KeyError, match="Available: \\['local_dev'\\]"):
        manager.get_cluster_config("missing")


def test_password_can_come_from_environment(tmp_path, monkeypatch):
    config_path = write_config(
        tmp_path / ".arango",
        """
clusters:
  cloud:
    endpoint: "https://example.arangodb.cloud:8529"
    password_env: "TEST_CLOUD_PASSWORD"
""",
    )
    manager = ArangoCredentialManager(str(config_path))

    monkeypatch.delenv("TEST_CLOUD_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="TEST_CLOUD_PASSWORD"):
        manager.get_connection_params("cloud")

    monkeypatch.setenv("TEST_CLOUD_PASSWORD", "from-env")
    assert manager.get_connection_params("cloud")["password"] == "from-env"


def test_mask_secret_hides_value_and_length():
    assert mask_secret("short") == mask_secret("a-much-longer-sample-value")
    assert "short" not in mask_secret("short")
    assert mask_secret("") == ""


def fake_docker(returncode=0, stdout="", stderr=""):
    def run(cmd, **kwargs):
        run.cmd = cmd
        return subprocess.CompletedProcess(cmd, returncode, stdout, stderr)

    return run


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ({"stdout": "true\n"}, "running"),
        ({"stdout": "false\n"}, "stopped"),
        ({"returncode": 1, "stderr": "Error: No such object: ontology-arango"}, "not_found"),
        ({"returncode": 1, "stderr": "Cannot connect to the Docker daemon"}, "docker_unavailable"),
    ],
)
def test_docker_status_uses_exact_container_name(tmp_path, monkeypatch, result, expected):
    manager = ArangoCredentialManager(str(write_config(tmp_path / ".arango", LOCAL_DEV)))
    run = fake_docker(**result)
    monkeypatch.setattr(subprocess, "run", run)

    assert manager.check_docker_container_status("local_dev") == expected
    assert run.cmd[:2] == ["docker", "inspect"]
    assert run.cmd[-1] == "ontology-arango"


def test_docker_status_when_docker_is_not_installed(tmp_path, monkeypatch):
    manager = ArangoCredentialManager(str(write_config(tmp_path / ".arango", LOCAL_DEV)))

    def missing(*args, **kwargs):
        raise FileNotFoundError("docker")

    monkeypatch.setattr(subprocess, "run", missing)

    assert manager.check_docker_container_status("local_dev") == "docker_unavailable"
