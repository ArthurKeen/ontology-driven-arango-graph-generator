#!/usr/bin/env python3
"""
Demo script for ArangoDB cluster management functionality.
Shows how the credential system integrates with the transformation tool.
"""

import argparse
import sys

try:
    from .arango_credentials import ArangoCredentialManager
except ImportError:
    from arango_credentials import ArangoCredentialManager


def mask_secret(secret: str) -> str:
    """Return a fixed mask for non-empty secrets."""
    return "*" * len(secret) if secret else ""


def main():
    parser = argparse.ArgumentParser(
        description="Demo ArangoDB Cluster Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Cluster Management Examples:
  python demo_cluster_management.py --list-clusters
  python demo_cluster_management.py --cluster local_dev --test-connection
  python demo_cluster_management.py --cluster local_dev --start-container
        """,
    )

    # Cluster management arguments
    parser.add_argument(
        "--list-clusters", action="store_true", help="List available ArangoDB clusters and exit"
    )
    parser.add_argument("--cluster", help="Cluster ID to use (from .arango file)")
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection parameters for specified cluster",
    )
    parser.add_argument(
        "--start-container",
        action="store_true",
        help="Start Docker container for specified cluster (if applicable)",
    )
    parser.add_argument(
        "--config", default=".arango", help="Path to ArangoDB configuration file (default: .arango)"
    )

    args = parser.parse_args()

    # Initialize credential manager
    try:
        credential_manager = ArangoCredentialManager(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error loading configuration: {e}")
        print(f"   Make sure {args.config} exists and is properly formatted.")
        sys.exit(1)

    # Handle list clusters command
    if args.list_clusters:
        credential_manager.print_cluster_summary()
        return

    # Require cluster specification for other commands
    if not args.cluster:
        print("❌ Error: --cluster is required for connection operations.")
        print("   Use --list-clusters to see available clusters.")
        sys.exit(1)

    # Validate cluster exists
    try:
        cluster_config = credential_manager.get_cluster_config(args.cluster)
        print(f"🎯 Selected cluster: {cluster_config['name']} ({args.cluster})")
    except KeyError as e:
        print(f"❌ Error: {e}")
        print("   Use --list-clusters to see available clusters.")
        sys.exit(1)

    # Handle start container command
    if args.start_container:
        if not credential_manager.is_docker_cluster(args.cluster):
            print(f"❌ Error: Cluster '{args.cluster}' is not a Docker cluster.")
            return

        container_status = credential_manager.check_docker_container_status(args.cluster)
        container_name = credential_manager.get_container_name(args.cluster)

        if container_status == "not_found":
            print(f"❌ Docker container '{container_name}' not found!")
            print("   Please ensure the container exists and try again.")
        elif container_status == "running":
            print(f"✅ Docker container '{container_name}' is already running")
        elif container_status == "stopped":
            print(f"🚀 Starting Docker container '{container_name}'...")
            if credential_manager.start_docker_container(args.cluster):
                print(f"✅ Container '{container_name}' started successfully")
            else:
                print(f"❌ Failed to start container '{container_name}'")
        return

    # Handle test connection command
    if args.test_connection:
        try:
            conn_params = credential_manager.get_connection_params(args.cluster)
            print(f"\n🔗 Connection Parameters for '{args.cluster}':")
            print(f"   Host: {conn_params['host']}")
            print(f"   Port: {conn_params['port']}")
            print(f"   Username: {conn_params['username']}")
            print(f"   Password: {mask_secret(conn_params['password'])}")
            print(f"   Database: {conn_params['database']}")
            print(f"   SSL: {conn_params['use_ssl']}")

            # Show Docker status if applicable
            if credential_manager.is_docker_cluster(args.cluster):
                container_status = credential_manager.check_docker_container_status(args.cluster)
                container_name = credential_manager.get_container_name(args.cluster)
                print(f"   Container: {container_name} ({container_status})")

                if container_status == "stopped":
                    print("\n⚠️  Container is stopped. Use --start-container to start it.")
                elif container_status == "not_found":
                    print("\n❌ Container not found. Please check Docker setup.")

        except Exception as e:
            print(f"❌ Error getting connection parameters: {e}")
        return

    # Default action if no specific command
    print("ℹ️  No action specified. Use --help to see available commands.")


if __name__ == "__main__":
    main()
