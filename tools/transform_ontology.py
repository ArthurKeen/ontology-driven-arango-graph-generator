#!/usr/bin/env python3
"""
Transform any ontology (OWL/RDF) to ArangoDB Graph Models using ArangoRDF.
Supports multiple graph model transformations:
- RPT (RDF Preserving Transformation) - Preserves complete RDF semantics
- PGT (Property Graph Transformation) - Optimized property graph with vertex/edge collections
- LPGT (Labeled Property Graph Transformation) - Labeled property graph with rich schema
"""

import os
import argparse
import sys
from typing import Optional

# Handle missing dependencies gracefully
try:
    from rdflib import Graph
except ImportError:
    print("❌ Error: rdflib not installed. Install with: pip install rdflib>=6.0.0")
    sys.exit(1)

try:
    from arangordf.arangodb import ArangoDB
    from arangordf.transformers import RPT, PGT, LPGT
    ARANGORDF_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: arangordf not installed. Some features may be limited.")
    print("   Install with: pip install arangordf>=0.1.0")
    ARANGORDF_AVAILABLE = False
    # Create placeholder classes for argument parsing
    class ArangoDB: pass
    class RPT: pass  
    class PGT: pass
    class LPGT: pass

try:
    from arango_credentials import ArangoCredentialManager
except ImportError:
    print("❌ Error: arango_credentials module not found.")
    print("   Make sure you're running from the project root directory.")
    sys.exit(1)

class OntologyGraphTransformer:
    def __init__(self, cluster_id: str = None, credential_manager: ArangoCredentialManager = None,
                 host: str = None, port: int = None, username: str = None, 
                 password: str = None, database: str = None):
        """Initialize the transformer with ArangoDB connection details."""
        
        if cluster_id and credential_manager:
            # New cluster-based initialization
            self.cluster_id = cluster_id
            self.credential_manager = credential_manager
            
            # Get connection parameters from credential manager
            conn_params = credential_manager.get_connection_params(cluster_id)
            
            # Check if it's a Docker container and start if needed
            if credential_manager.is_docker_cluster(cluster_id):
                self._ensure_docker_container_running()
            
            self.arangodb = ArangoDB(
                host=conn_params['host'],
                port=conn_params['port'],
                username=conn_params['username'],
                password=conn_params['password'],
                database=conn_params['database']
            )
            database_name = conn_params['database']
            
        else:
            # Legacy direct parameter initialization
            self.cluster_id = None
            self.credential_manager = None
            
            self.arangodb = ArangoDB(
                host=host or "localhost",
                port=port or 8529,
                username=username or "root",
                password=password or "",
                database=database or "graph_ontology"
            )
            database_name = database or "graph_ontology"
        
        # Ensure the database exists
        if not self.arangodb.has_database(database_name):
            self.arangodb.create_database(database_name)
    
    def _ensure_docker_container_running(self):
        """Ensure Docker container is running for Docker-based clusters."""
        container_status = self.credential_manager.check_docker_container_status(self.cluster_id)
        container_name = self.credential_manager.get_container_name(self.cluster_id)
        
        if container_status == 'not_found':
            print(f"⚠️  Docker container '{container_name}' not found!")
            print(f"   Please ensure the container exists and try again.")
            sys.exit(1)
        elif container_status == 'stopped':
            print(f"🚀 Starting Docker container '{container_name}'...")
            if self.credential_manager.start_docker_container(self.cluster_id):
                print(f"✅ Container '{container_name}' started successfully")
                # Wait a moment for the container to be ready
                import time
                time.sleep(3)
            else:
                print(f"❌ Failed to start container '{container_name}'")
                sys.exit(1)
        elif container_status == 'running':
            print(f"✅ Docker container '{container_name}' is already running")

    def load_ontology(self, owl_file: str, ttl_file: Optional[str] = None) -> Graph:
        """
        Load the ontology from OWL and optionally TTL files into an RDF graph.
        
        Args:
            owl_file: Path to the OWL file
            ttl_file: Optional path to the TTL file with examples
            
        Returns:
            RDFlib Graph containing the ontology
        """
        graph = Graph()
        
        # Load OWL ontology
        graph.parse(owl_file, format="xml")
        
        # Load TTL examples if provided
        if ttl_file and os.path.exists(ttl_file):
            graph.parse(ttl_file, format="turtle")
            
        return graph

    def transform_rpt(self, graph: Graph, prefix: str = "rpt") -> None:
        """
        Apply Resource Pattern Transformation.
        Creates a simple graph where each RDF resource becomes a vertex.
        """
        transformer = RPT(
            arangodb=self.arangodb,
            graph_name=f"{prefix}_aws_graph",
            vertex_collection=f"{prefix}_vertices",
            edge_collection=f"{prefix}_edges"
        )
        transformer.transform(graph)

    def transform_pgt(self, graph: Graph, prefix: str = "pgt") -> None:
        """
        Apply Property Graph Transformation.
        Creates a property graph with RDF properties as edge attributes.
        """
        transformer = PGT(
            arangodb=self.arangodb,
            graph_name=f"{prefix}_aws_graph",
            vertex_collection=f"{prefix}_vertices",
            edge_collection=f"{prefix}_edges"
        )
        transformer.transform(graph)

    def transform_lpgt(self, graph: Graph, prefix: str = "lpgt") -> None:
        """
        Apply Labeled Property Graph Transformation.
        Creates a labeled property graph preserving RDF semantics.
        """
        transformer = LPGT(
            arangodb=self.arangodb,
            graph_name=f"{prefix}_aws_graph",
            vertex_collection=f"{prefix}_vertices",
            edge_collection=f"{prefix}_edges"
        )
        transformer.transform(graph)

def test_cluster_connection(cluster_id: str, credential_manager: ArangoCredentialManager):
    """Test connection to a specific cluster."""
    try:
        cluster_config = credential_manager.get_cluster_config(cluster_id)
        print(f"🎯 Testing connection to: {cluster_config['name']} ({cluster_id})")
        
        # Check Docker container status if applicable
        if credential_manager.is_docker_cluster(cluster_id):
            container_status = credential_manager.check_docker_container_status(cluster_id)
            container_name = credential_manager.get_container_name(cluster_id)
            print(f"   Docker container: {container_name} ({container_status})")
            
            if container_status == 'stopped':
                print(f"⚠️  Container is stopped. Starting container...")
                if credential_manager.start_docker_container(cluster_id):
                    print(f"✅ Container '{container_name}' started successfully")
                    import time
                    time.sleep(3)  # Wait for container to be ready
                else:
                    print(f"❌ Failed to start container '{container_name}'")
                    return False
            elif container_status == 'not_found':
                print(f"❌ Container '{container_name}' not found!")
                return False
        
        # Test connection if arangordf is available
        if ARANGORDF_AVAILABLE:
            try:
                transformer = OntologyGraphTransformer(cluster_id, credential_manager)
                print("✅ Connection test successful!")
                return True
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
                return False
        else:
            conn_params = credential_manager.get_connection_params(cluster_id)
            print(f"⚠️  arangordf not available - showing connection parameters:")
            print(f"   Host: {conn_params['host']}:{conn_params['port']}")
            print(f"   Username: {conn_params['username']}")
            print(f"   Database: {conn_params['database']}")
            print(f"   SSL: {conn_params['use_ssl']}")
            return True
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_legacy_connection(args):
    """Test legacy connection parameters."""
    print("🎯 Testing legacy connection parameters...")
    
    if ARANGORDF_AVAILABLE:
        try:
            transformer = OntologyGraphTransformer(
                host=args.host or "localhost",
                port=args.port or 8529,
                username=args.username or "root", 
                password=args.password or "",
                database=args.database or "graph_ontology"
            )
            print("✅ Legacy connection test successful!")
            return True
        except Exception as e:
            print(f"❌ Legacy connection test failed: {e}")
            return False
    else:
        print("⚠️  arangordf not available - cannot test connection")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Transform any ontology to ArangoDB graph models using different patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Cluster Management:
  Use --list-clusters to see available ArangoDB clusters
  Use --cluster to specify which cluster to use (defaults to configured default)
  Use --test-connection to test connectivity before transformation
  Use --setup-deps to install missing dependencies
  
Examples:
  python transform_ontology.py --setup-deps
  python transform_ontology.py --list-clusters
  python transform_ontology.py --cluster project_a_local --test-connection
  python transform_ontology.py --cluster project_a_local --patterns pgt
  python transform_ontology.py --cluster project_a_cloud --patterns pgt lpgt
        """
    )
    
    # Cluster management arguments
    parser.add_argument(
        "--list-clusters", 
        action="store_true", 
        help="List available ArangoDB clusters and exit"
    )
    parser.add_argument(
        "--cluster", 
        help="Cluster ID to use (from .arango file). If not specified, uses default cluster"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to specified cluster and exit"
    )
    parser.add_argument(
        "--setup-deps",
        action="store_true",
        help="Install missing dependencies and exit"
    )
    parser.add_argument(
        "--start-container",
        action="store_true",
        help="Start Docker container for specified cluster (if applicable)"
    )
    parser.add_argument(
        "--config", 
        default=".arango", 
        help="Path to ArangoDB configuration file (default: .arango)"
    )
    
    # Legacy connection arguments (deprecated but kept for backward compatibility)
    parser.add_argument("--host", help="ArangoDB host (deprecated: use --cluster instead)")
    parser.add_argument("--port", type=int, help="ArangoDB port (deprecated: use --cluster instead)")
    parser.add_argument("--username", help="ArangoDB username (deprecated: use --cluster instead)")
    parser.add_argument("--password", help="ArangoDB password (deprecated: use --cluster instead)")
    parser.add_argument("--database", help="Database name (deprecated: use --cluster instead)")
    
    # Transformation options
    parser.add_argument("--owl", default="ontology/ontology.owl", help="Path to OWL ontology file")
    parser.add_argument("--ttl", default="ontology/sample_data.ttl", help="Path to TTL sample data file")
    parser.add_argument(
        "--patterns",
        nargs="+",
        choices=["rpt", "pgt", "lpgt"],
        default=["pgt"],
        help="Transformation patterns to apply (default: pgt)"
    )

    args = parser.parse_args()
    
    # Handle setup dependencies command first (doesn't need credential manager)
    if args.setup_deps:
        import subprocess
        print("🔧 Installing missing dependencies...")
        try:
            subprocess.run([sys.executable, "tools/setup_environment.py", "--install-deps"], check=True)
            print("✅ Dependencies setup completed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. See output above for details.")
            sys.exit(1)
        return
    
    # Initialize credential manager
    try:
        credential_manager = ArangoCredentialManager(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error loading configuration: {e}")
        print(f"   Make sure {args.config} exists and is properly formatted.")
        print(f"   Run: python tools/setup_environment.py to validate your setup")
        sys.exit(1)
    
    # Handle list clusters command
    if args.list_clusters:
        credential_manager.print_cluster_summary()
        return
    
    # Determine which cluster to use
    if args.cluster:
        cluster_id = args.cluster
        
        # Validate cluster exists
        try:
            cluster_config = credential_manager.get_cluster_config(cluster_id)
        except KeyError as e:
            print(f"❌ Error: {e}")
            print("   Use --list-clusters to see available clusters.")
            sys.exit(1)
            
    elif any([args.test_connection, args.start_container]):
        print("❌ Error: --cluster is required for connection operations.")
        print("   Use --list-clusters to see available clusters.")
        sys.exit(1)
    else:
        # Check if legacy arguments are used
        if any([args.host, args.port, args.username, args.password, args.database]):
            print("⚠️  Warning: Legacy connection arguments detected.")
            print("   Consider migrating to cluster-based configuration in .arango file.")
            print("   Using legacy mode for this run.\\n")
            
            # For legacy mode, we'll handle this later
            cluster_id = None
        else:
            # Use default cluster
            try:
                cluster_id = credential_manager.get_default_cluster()
                print(f"🎯 Using default cluster: {cluster_id}")
            except ValueError as e:
                print(f"❌ Error: {e}")
                print("   Use --list-clusters to see available clusters.")
                sys.exit(1)
    
    # Handle start container command
    if args.start_container:
        if not credential_manager.is_docker_cluster(cluster_id):
            print(f"❌ Error: Cluster '{cluster_id}' is not a Docker cluster.")
            sys.exit(1)
        
        container_status = credential_manager.check_docker_container_status(cluster_id)
        container_name = credential_manager.get_container_name(cluster_id)
        
        if container_status == 'not_found':
            print(f"❌ Docker container '{container_name}' not found!")
            print(f"   Please ensure the container exists and try again.")
            sys.exit(1)
        elif container_status == 'running':
            print(f"✅ Docker container '{container_name}' is already running")
        elif container_status == 'stopped':
            print(f"🚀 Starting Docker container '{container_name}'...")
            if credential_manager.start_docker_container(cluster_id):
                print(f"✅ Container '{container_name}' started successfully")
            else:
                print(f"❌ Failed to start container '{container_name}'")
                sys.exit(1)
        return
    
    # Handle test connection command
    if args.test_connection:
        if cluster_id:
            test_cluster_connection(cluster_id, credential_manager)
        else:
            # Legacy mode connection test
            test_legacy_connection(args)
        return
    
    # Check if arangordf is available for transformations
    if not ARANGORDF_AVAILABLE:
        print("❌ Error: arangordf library is required for transformations.")
        print("   Install with: pip install arangordf>=0.1.0")
        print("   Or run: python tools/transform_ontology.py --setup-deps")
        sys.exit(1)

    # Initialize transformer with cluster-based configuration
    if not any([args.host, args.port, args.username, args.password, args.database]):
        try:
            cluster_config = credential_manager.get_cluster_config(cluster_id)
            print(f"🔗 Connecting to cluster: {cluster_config['name']} ({cluster_id})")
            transformer = OntologyGraphTransformer(cluster_id, credential_manager)
        except KeyError as e:
            print(f"❌ Error: {e}")
            print("   Use --list-clusters to see available clusters.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error connecting to cluster '{cluster_id}': {e}")
            sys.exit(1)
    else:
        # Legacy transformer creation
        print("⚠️  Warning: Using legacy connection mode.")
        transformer = OntologyGraphTransformer(
            host=args.host or "localhost",
            port=args.port or 8529,
            username=args.username or "root",
            password=args.password or "",
            database=args.database or "graph_ontology"
        )

    # Load ontology
    print(f"📖 Loading ontology from {args.owl}...")
    graph = transformer.load_ontology(args.owl, args.ttl)
    print(f"✅ Loaded {len(graph)} triples from ontology")

    # Apply requested transformations
    print(f"\n🔄 Applying transformations: {', '.join(args.patterns).upper()}")
    
    if "rpt" in args.patterns:
        print("\n📊 Applying RPT (RDF Preserving Transformation)...")
        transformer.transform_rpt(graph)
        print("✅ RPT transformation completed")

    if "pgt" in args.patterns:
        print("\n📊 Applying PGT (Property Graph Transformation)...")
        transformer.transform_pgt(graph)
        print("✅ PGT transformation completed")

    if "lpgt" in args.patterns:
        print("\n📊 Applying LPGT (Labeled Property Graph Transformation)...")
        transformer.transform_lpgt(graph)
        print("✅ LPGT transformation completed")

    print("\n🎉 All transformations completed successfully!")

if __name__ == "__main__":
    main() 