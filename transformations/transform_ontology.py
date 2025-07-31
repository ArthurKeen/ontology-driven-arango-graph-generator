#!/usr/bin/env python3
"""
Transform AWS Ontology to ArangoDB Graph Schema using ArangoRDF.
Supports multiple transformation patterns:
- RPT (Resource Pattern Transformation)
- PGT (Property Graph Transformation)
- LPGT (Labeled Property Graph Transformation)
"""

import os
import argparse
from typing import Optional
from rdflib import Graph
from arangordf.arangodb import ArangoDB
from arangordf.transformers import RPT, PGT, LPGT

class AWSOntologyTransformer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8529,
        username: str = "root",
        password: str = "",
        database: str = "aws_ontology"
    ):
        """Initialize the transformer with ArangoDB connection details."""
        self.arangodb = ArangoDB(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database
        )
        
        # Ensure the database exists
        if not self.arangodb.has_database(database):
            self.arangodb.create_database(database)

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

def main():
    parser = argparse.ArgumentParser(
        description="Transform AWS Ontology to ArangoDB using different patterns"
    )
    
    # Database connection arguments
    parser.add_argument("--host", default="localhost", help="ArangoDB host")
    parser.add_argument("--port", type=int, default=8529, help="ArangoDB port")
    parser.add_argument("--username", default="root", help="ArangoDB username")
    parser.add_argument("--password", default="", help="ArangoDB password")
    parser.add_argument("--database", default="aws_ontology", help="Database name")
    
    # Transformation options
    parser.add_argument("--owl", default="ontology/aws.owl", help="Path to OWL file")
    parser.add_argument("--ttl", default="ontology/examples.ttl", help="Path to TTL examples")
    parser.add_argument(
        "--patterns",
        nargs="+",
        choices=["rpt", "pgt", "lpgt"],
        default=["rpt", "pgt", "lpgt"],
        help="Transformation patterns to apply"
    )

    args = parser.parse_args()

    # Initialize transformer
    transformer = AWSOntologyTransformer(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        database=args.database
    )

    # Load ontology
    graph = transformer.load_ontology(args.owl, args.ttl)

    # Apply requested transformations
    if "rpt" in args.patterns:
        print("Applying RPT transformation...")
        transformer.transform_rpt(graph)

    if "pgt" in args.patterns:
        print("Applying PGT transformation...")
        transformer.transform_pgt(graph)

    if "lpgt" in args.patterns:
        print("Applying LPGT transformation...")
        transformer.transform_lpgt(graph)

    print("Transformations completed successfully!")

if __name__ == "__main__":
    main() 