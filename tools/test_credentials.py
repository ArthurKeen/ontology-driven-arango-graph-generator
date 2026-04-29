#!/usr/bin/env python3
"""
Test script for ArangoDB credentials manager.
"""

try:
    from .arango_credentials import ArangoCredentialManager
except ImportError:
    from arango_credentials import ArangoCredentialManager


def main():
    try:
        # Initialize credential manager
        manager = ArangoCredentialManager()

        # Test listing clusters
        print("Testing credential manager...")
        manager.print_cluster_summary()

        # Test getting connection params for default cluster
        default_cluster = manager.get_default_cluster()
        print(f"\nDefault cluster: {default_cluster}")

        conn_params = manager.get_connection_params(default_cluster)
        safe_params = dict(conn_params)
        if safe_params.get("password"):
            safe_params["password"] = "*" * len(safe_params["password"])
        print(f"Connection params: {safe_params}")

        # Test Docker container status if applicable
        if manager.is_docker_cluster(default_cluster):
            status = manager.check_docker_container_status(default_cluster)
            print(f"Docker container status: {status}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
