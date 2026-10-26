"""
ArangoDB credential manager for ontology transformation projects.

Manages multiple ArangoDB cluster configurations from a local .arango file.
Supports both Docker and cloud instances with credential management.
"""

import os
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

import yaml

DEFAULT_DATABASE = "graph_ontology"


def mask_secret(secret: str | None) -> str:
    """Return a fixed-width mask so output reveals neither the secret nor its length."""
    return "********" if secret else ""


def wait_for_endpoint(endpoint: str, timeout: float = 60.0, interval: float = 1.0) -> bool:
    """
    Wait until an ArangoDB server answers HTTP requests.

    Any HTTP response, including 401, means the server is up and accepting connections.

    Returns:
        True if the server answered before the timeout, False otherwise
    """
    deadline = time.monotonic() + timeout
    url = endpoint.rstrip("/") + "/_api/version"
    while True:
        try:
            with urllib.request.urlopen(url, timeout=interval):
                return True
        except urllib.error.HTTPError:
            return True
        except (urllib.error.URLError, OSError):
            pass
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)


class ArangoCredentialManager:
    """Manages ArangoDB cluster configurations from .arango file."""

    def __init__(self, config_path: str = ".arango"):
        """
        Initialize the credential manager.

        Args:
            config_path: Path to the .arango configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load and validate configuration from .arango file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}") from e

        if not isinstance(config, dict) or "clusters" not in config:
            raise ValueError("Invalid configuration: missing 'clusters' section")
        if not isinstance(config["clusters"], dict) or not config["clusters"]:
            raise ValueError("Invalid configuration: 'clusters' must be a non-empty mapping")

        for cluster_id, cluster_config in config["clusters"].items():
            if not isinstance(cluster_config, dict) or not cluster_config.get("endpoint"):
                raise ValueError(f"Invalid configuration: cluster '{cluster_id}' needs an endpoint")
            if cluster_config.get("type") == "docker" and not cluster_config.get("container_name"):
                raise ValueError(
                    f"Invalid configuration: docker cluster '{cluster_id}' needs a container_name"
                )

        default = config.get("default")
        if default is not None and default not in config["clusters"]:
            raise ValueError(f"Invalid configuration: default cluster '{default}' is not defined")

        return config

    def list_clusters(self) -> list[dict[str, str]]:
        """
        List all available clusters with their basic information.

        Returns:
            List of cluster info dictionaries
        """
        clusters = []
        for cluster_id, cluster_config in self.config["clusters"].items():
            clusters.append(
                {
                    "id": cluster_id,
                    "name": cluster_config.get("name", cluster_id),
                    "type": cluster_config.get("type", "unknown"),
                    "endpoint": cluster_config["endpoint"],
                }
            )
        return clusters

    def get_cluster_config(self, cluster_id: str) -> dict[str, Any]:
        """
        Get configuration for a specific cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            Complete cluster configuration

        Raises:
            KeyError: If cluster_id is not found
        """
        if cluster_id not in self.config["clusters"]:
            available = list(self.config["clusters"].keys())
            raise KeyError(f"Cluster '{cluster_id}' not found. Available: {available}")

        return self.config["clusters"][cluster_id]

    def get_password(self, cluster_id: str) -> str:
        """
        Resolve the password for a cluster.

        A cluster may set ``password_env`` to read the password from an environment
        variable instead of storing it in the .arango file.

        Raises:
            ValueError: If ``password_env`` names a variable that is not set
        """
        cluster_config = self.get_cluster_config(cluster_id)
        env_var = cluster_config.get("password_env")
        if env_var:
            if env_var not in os.environ:
                raise ValueError(
                    f"Cluster '{cluster_id}' reads its password from ${env_var}, which is not set"
                )
            return os.environ[env_var]
        return cluster_config.get("password", "")

    def get_connection_params(self, cluster_id: str) -> dict[str, Any]:
        """
        Get ArangoDB connection parameters for a specific cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            Dictionary with connection parameters compatible with ArangoDB client
        """
        cluster_config = self.get_cluster_config(cluster_id)
        endpoint = cluster_config["endpoint"]
        parsed_url = urlparse(endpoint)

        return {
            "endpoint": endpoint,
            "host": parsed_url.hostname or "localhost",
            "port": parsed_url.port or 8529,
            "username": cluster_config.get("username", "root"),
            "password": self.get_password(cluster_id),
            "database": cluster_config.get("database", DEFAULT_DATABASE),
            "use_ssl": parsed_url.scheme == "https",
        }

    def get_default_cluster(self) -> str:
        """Get the default cluster ID, falling back to the first configured cluster."""
        default = self.config.get("default")
        if default is not None:
            return default
        return next(iter(self.config["clusters"]))

    def is_docker_cluster(self, cluster_id: str) -> bool:
        """Check if a cluster is a Docker-based cluster."""
        cluster_config = self.get_cluster_config(cluster_id)
        return cluster_config.get("type") == "docker"

    def get_container_name(self, cluster_id: str) -> str | None:
        """Get Docker container name for a cluster (if it's a Docker cluster)."""
        if not self.is_docker_cluster(cluster_id):
            return None

        cluster_config = self.get_cluster_config(cluster_id)
        return cluster_config.get("container_name")

    def check_docker_container_status(self, cluster_id: str) -> str | None:
        """
        Check the state of the Docker container for a Docker-based cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            'running', 'stopped', 'not_found', 'docker_unavailable', or None if not Docker
        """
        container_name = self.get_container_name(cluster_id)
        if not container_name:
            return None

        try:
            # `docker inspect` matches the exact container name, unlike `docker ps --filter`
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Running}}", container_name],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return "docker_unavailable"

        if result.returncode != 0:
            if "no such" in result.stderr.lower():
                return "not_found"
            return "docker_unavailable"

        return "running" if result.stdout.strip() == "true" else "stopped"

    def start_docker_container(self, cluster_id: str) -> bool:
        """
        Start Docker container for a Docker-based cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            True if successful, False otherwise
        """
        container_name = self.get_container_name(cluster_id)
        if not container_name:
            return False

        try:
            subprocess.run(["docker", "start", container_name], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def print_cluster_summary(self) -> None:
        """Print a formatted summary of all clusters."""
        clusters = self.list_clusters()
        default_cluster = self.get_default_cluster()

        print("\n🗂️  Available ArangoDB Clusters:")
        print("=" * 50)

        for cluster in clusters:
            status_info = ""

            # Add Docker status if applicable
            if cluster["type"] == "docker":
                container_status = self.check_docker_container_status(cluster["id"])
                status_info = {
                    "running": " 🟢 Running",
                    "stopped": " 🔴 Stopped",
                    "not_found": " ❓ Not Found",
                    "docker_unavailable": " ⚠️  Docker unavailable",
                }.get(container_status, "")

            # Mark default cluster
            default_mark = " ⭐ Default" if cluster["id"] == default_cluster else ""

            print(
                f"  📊 {cluster['id']:<20} | {cluster['name']:<25} | {cluster['type']:<8}{status_info}{default_mark}"
            )
            print(f"     {cluster['endpoint']}")
            print()
