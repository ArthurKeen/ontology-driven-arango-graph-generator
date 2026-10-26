"""
Command-line interface for transforming ontologies into ArangoDB graph models.

Connections come from a cluster in the .arango file, or directly from --endpoint
with the password in the ARANGO_PASSWORD environment variable.
"""

import argparse
import logging
import os
import sys

from . import __version__
from .arango_credentials import ArangoCredentialManager, mask_secret, wait_for_endpoint
from .transformer import PATTERNS, OntologyGraphTransformer, load_ontology

PASSWORD_ENV_VAR = "ARANGO_PASSWORD"


class CLIError(Exception):
    """An error with a message that is shown to the user without a traceback."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ontology-transform",
        description="Transform any ontology to ArangoDB graph models using different patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  ontology-transform --list-clusters
  ontology-transform --cluster local_dev --test-connection
  ontology-transform --cluster local_dev --owl examples/ontology.owl --ttl examples/sample_data.ttl
  ontology-transform --cluster local_dev --owl my.owl --patterns pgt lpgt --overwrite

Direct connection without a .arango file:
  export {PASSWORD_ENV_VAR}=...
  ontology-transform --endpoint http://localhost:8529 --owl examples/ontology.owl
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs")

    target = parser.add_argument_group("connection")
    target.add_argument(
        "--config", default=".arango", help="Path to ArangoDB configuration file (default: .arango)"
    )
    target.add_argument(
        "--list-clusters", action="store_true", help="List available ArangoDB clusters and exit"
    )
    target.add_argument(
        "--cluster",
        help="Cluster ID to use (from .arango file). If not specified, uses default cluster",
    )
    target.add_argument(
        "--endpoint",
        help=f"Connect directly to this URL instead of a configured cluster "
        f"(password from ${PASSWORD_ENV_VAR})",
    )
    target.add_argument(
        "--username", default="root", help="Username for --endpoint connections (default: root)"
    )
    target.add_argument(
        "--database", help="Database name (overrides the cluster's configured database)"
    )
    target.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to the selected cluster or endpoint and exit",
    )
    target.add_argument(
        "--start-container",
        action="store_true",
        help="Start the Docker container for the selected cluster and exit",
    )

    transform = parser.add_argument_group("transformation")
    transform.add_argument("--owl", help="Path to the ontology file (RDF/XML, Turtle, ...)")
    transform.add_argument("--ttl", help="Optional path to sample instance data")
    transform.add_argument(
        "--rdf-format",
        help="rdflib format for both files (default: guessed from the file, e.g. xml, turtle)",
    )
    transform.add_argument(
        "--patterns",
        nargs="+",
        choices=list(PATTERNS),
        default=["pgt"],
        help="Transformation patterns to apply (default: pgt)",
    )
    transform.add_argument(
        "--graph-name",
        default="ontology_graph",
        help="Base graph name; each pattern writes <pattern>_<graph-name> (default: ontology_graph)",
    )
    transform.add_argument(
        "--overwrite",
        action="store_true",
        help="Drop existing graphs and their collections before importing",
    )
    return parser


def ensure_container_running(manager: ArangoCredentialManager, cluster_id: str) -> None:
    """Start a Docker cluster's container if needed and wait until ArangoDB answers."""
    status = manager.check_docker_container_status(cluster_id)
    container_name = manager.get_container_name(cluster_id)

    if status == "docker_unavailable":
        raise CLIError("Docker is not installed or the Docker daemon is not running.")
    if status == "not_found":
        raise CLIError(
            f"Docker container '{container_name}' not found. "
            "Create it first, for example with: docker compose up -d"
        )
    if status == "running":
        print(f"✅ Docker container '{container_name}' is running")
        return

    print(f"🚀 Starting Docker container '{container_name}'...")
    if not manager.start_docker_container(cluster_id):
        raise CLIError(f"Failed to start container '{container_name}'")

    endpoint = manager.get_cluster_config(cluster_id)["endpoint"]
    if not wait_for_endpoint(endpoint):
        raise CLIError(f"Container '{container_name}' started but {endpoint} is not responding")
    print(f"✅ Container '{container_name}' started successfully")


def connect(args: argparse.Namespace) -> OntologyGraphTransformer:
    """Connect to the database selected by the command-line arguments."""
    if args.endpoint:
        password = os.environ.get(PASSWORD_ENV_VAR, "")
        database = args.database or "graph_ontology"
        print(f"🔗 Connecting to {args.endpoint} (database: {database})")
        return OntologyGraphTransformer.connect(args.endpoint, args.username, password, database)

    manager, cluster_id = select_cluster(args)
    cluster_config = manager.get_cluster_config(cluster_id)
    print(f"🔗 Connecting to cluster: {cluster_config.get('name', cluster_id)} ({cluster_id})")
    if manager.is_docker_cluster(cluster_id):
        ensure_container_running(manager, cluster_id)
    return OntologyGraphTransformer.from_cluster(manager, cluster_id, database=args.database)


def load_manager(args: argparse.Namespace) -> ArangoCredentialManager:
    try:
        return ArangoCredentialManager(args.config)
    except FileNotFoundError as e:
        raise CLIError(
            f"{e}. Copy .arango.example to {args.config}, or use --endpoint for a direct connection."
        ) from e


def select_cluster(args: argparse.Namespace):
    manager = load_manager(args)
    cluster_id = args.cluster or manager.get_default_cluster()
    try:
        manager.get_cluster_config(cluster_id)
    except KeyError as e:
        raise CLIError(f"{e.args[0]}. Use --list-clusters to see available clusters.") from e
    return manager, cluster_id


def check_connection(args: argparse.Namespace) -> None:
    if not args.endpoint:
        manager, cluster_id = select_cluster(args)
        params = manager.get_connection_params(cluster_id)
        print(f"🎯 Testing connection to: {cluster_id}")
        print(f"   Endpoint: {params['endpoint']}")
        print(f"   Username: {params['username']}")
        print(f"   Password: {mask_secret(params['password'])}")
        print(f"   Database: {args.database or params['database']}")

    transformer = connect(args)
    version = transformer.db.version()
    print(f"✅ Connection test successful! (ArangoDB {version}, database: {transformer.db.name})")


def start_container(args: argparse.Namespace) -> None:
    manager, cluster_id = select_cluster(args)
    if not manager.is_docker_cluster(cluster_id):
        raise CLIError(f"Cluster '{cluster_id}' is not a Docker cluster.")
    ensure_container_running(manager, cluster_id)


def run_transformations(args: argparse.Namespace) -> None:
    # Load files before connecting so input mistakes fail fast
    print(f"📖 Loading ontology from {args.owl}...")
    graph = load_ontology(args.owl, args.ttl, args.rdf_format)
    print(f"✅ Loaded {len(graph)} triples")

    transformer = connect(args)

    for pattern in args.patterns:
        description, _ = PATTERNS[pattern]
        graph_name = f"{pattern}_{args.graph_name}"
        print(f"\n📊 Applying {pattern.upper()} ({description}) -> graph '{graph_name}'...")
        transformer.transform(graph, pattern, graph_name=graph_name, overwrite=args.overwrite)
        print(f"✅ {pattern.upper()} transformation completed")

    print("\n🎉 All transformations completed successfully!")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.endpoint and args.cluster:
        parser.error("--endpoint and --cluster cannot be used together")
    if args.endpoint and args.start_container:
        parser.error("--start-container requires a Docker cluster, not --endpoint")
    if not (args.list_clusters or args.test_connection or args.start_container or args.owl):
        parser.error("--owl is required to run a transformation")

    try:
        if args.list_clusters:
            load_manager(args).print_cluster_summary()
        elif args.start_container:
            start_container(args)
        elif args.test_connection:
            check_connection(args)
        else:
            run_transformations(args)
    except (CLIError, FileNotFoundError, PermissionError, ValueError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.verbose:
            raise
        print(f"❌ {type(e).__name__}: {e}", file=sys.stderr)
        print("   Re-run with --verbose for the full traceback.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
