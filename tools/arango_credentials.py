#!/usr/bin/env python3
"""
ArangoDB credential manager for ontology transformation projects.

Manages multiple ArangoDB cluster configurations from a local .arango file.
Supports both Docker and cloud instances with credential management.
"""

import os
import subprocess
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import yaml


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

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from .arango file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")

        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                if not config or "clusters" not in config:
                    raise ValueError("Invalid configuration: missing 'clusters' section")
                return config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}") from e

    def list_clusters(self) -> List[Dict[str, str]]:
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
                    "endpoint": cluster_config.get("endpoint", "N/A"),
                }
            )
        return clusters

    def get_cluster_config(self, cluster_id: str) -> Dict[str, Any]:
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

    def get_connection_params(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get ArangoDB connection parameters for a specific cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            Dictionary with connection parameters compatible with ArangoDB client
        """
        cluster_config = self.get_cluster_config(cluster_id)

        # Parse endpoint URL
        parsed_url = urlparse(cluster_config["endpoint"])

        return {
            "host": parsed_url.hostname or "localhost",
            "port": parsed_url.port or 8529,
            "username": cluster_config.get("username", "root"),
            "password": cluster_config.get("password", ""),
            "database": cluster_config.get("database", "graph_ontology"),
            "use_ssl": parsed_url.scheme == "https",
        }

    def get_default_cluster(self) -> str:
        """Get the default cluster ID from configuration."""
        default = self.config.get("default", "local")

        # Check if default cluster exists
        if default not in self.config["clusters"]:
            # Return first available cluster if default doesn't exist
            available_clusters = list(self.config["clusters"].keys())
            if available_clusters:
                return available_clusters[0]
            else:
                raise ValueError("No clusters configured")

        return default

    def is_docker_cluster(self, cluster_id: str) -> bool:
        """Check if a cluster is a Docker-based cluster."""
        cluster_config = self.get_cluster_config(cluster_id)
        return cluster_config.get("type") == "docker"

    def get_container_name(self, cluster_id: str) -> Optional[str]:
        """Get Docker container name for a cluster (if it's a Docker cluster)."""
        if not self.is_docker_cluster(cluster_id):
            return None

        cluster_config = self.get_cluster_config(cluster_id)
        return cluster_config.get("container_name")

    def check_docker_container_status(self, cluster_id: str) -> Optional[str]:
        """
        Check if Docker container is running for a Docker-based cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            Container status ('running', 'stopped', 'not_found') or None if not Docker
        """
        if not self.is_docker_cluster(cluster_id):
            return None

        container_name = self.get_container_name(cluster_id)
        if not container_name:
            return None

        try:
            # Check if container exists and its status
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                return "not_found"

            status = result.stdout.strip().lower()
            if "up" in status:
                return "running"
            else:
                return "stopped"

        except (subprocess.CalledProcessError, FileNotFoundError):
            return "not_found"

    def start_docker_container(self, cluster_id: str) -> bool:
        """
        Start Docker container for a Docker-based cluster.

        Args:
            cluster_id: The cluster identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.is_docker_cluster(cluster_id):
            return False

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
                if container_status == "running":
                    status_info = " 🟢 Running"
                elif container_status == "stopped":
                    status_info = " 🔴 Stopped"
                elif container_status == "not_found":
                    status_info = " ❓ Not Found"

            # Mark default cluster
            default_mark = " ⭐ Default" if cluster["id"] == default_cluster else ""

            print(
                f"  📊 {cluster['id']:<20} | {cluster['name']:<25} | {cluster['type']:<8}{status_info}{default_mark}"
            )
            print(f"     {cluster['endpoint']}")
            print()
