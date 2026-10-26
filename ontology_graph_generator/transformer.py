"""
Transform any ontology (OWL/RDF) to ArangoDB Graph Models using ArangoRDF.

Supports the graph model transformations provided by arango-rdf:
- RPT (RDF-topology Preserving Transformation) - Keeps the RDF statement structure
- PGT (Property Graph Transformation) - Property graph with per-class and per-predicate collections
- LPGT (Labeled Property Graph Transformation) - One Edge collection, edges labelled by predicate
"""

import logging
import os

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import DatabasePropertiesError
from arango.graph import Graph as ArangoGraph
from arango_rdf import ArangoRDF
from rdflib import Graph
from rdflib.util import guess_format

from .arango_credentials import ArangoCredentialManager

logger = logging.getLogger(__name__)

# ArangoDB error number for "database not found"
_ERROR_DATABASE_NOT_FOUND = 1228

# Formats tried when a file's extension is ambiguous (e.g. Turtle saved as .owl)
_FALLBACK_FORMATS = ["xml", "turtle", "json-ld", "nt"]

# CLI pattern name -> (description, ArangoRDF method)
PATTERNS = {
    "rpt": ("RDF-topology Preserving Transformation", "rdf_to_arangodb_by_rpt"),
    "pgt": ("Property Graph Transformation", "rdf_to_arangodb_by_pgt"),
    "lpgt": ("Labeled Property Graph Transformation", "rdf_to_arangodb_by_lpg"),
}


def _parse_into(graph: Graph, path: str, rdf_format: str | None) -> None:
    """Parse an RDF file into ``graph``, guessing its format when none is given."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"RDF file not found: {path}")

    if rdf_format:
        graph.parse(path, format=rdf_format)
        return

    guessed = guess_format(path)
    candidates = [guessed] if guessed else []
    candidates += [fmt for fmt in _FALLBACK_FORMATS if fmt not in candidates]

    first_error = None
    for fmt in candidates:
        attempt = Graph()
        try:
            attempt.parse(path, format=fmt)
        except Exception as e:
            first_error = first_error or e
            continue
        if fmt != guessed:
            logger.info("Parsed %s as %s", path, fmt)
        graph += attempt
        return

    raise ValueError(f"Could not parse {path} as any of {candidates}: {first_error}")


def load_ontology(
    owl_file: str, ttl_file: str | None = None, rdf_format: str | None = None
) -> Graph:
    """
    Load an ontology and optional instance data into a single RDF graph.

    Args:
        owl_file: Path to the ontology file (RDF/XML, Turtle, JSON-LD, N-Triples, ...)
        ttl_file: Optional path to a sample data file
        rdf_format: Force an rdflib format instead of guessing from the file

    Returns:
        RDFlib Graph containing the ontology and data

    Raises:
        FileNotFoundError: If either file does not exist
        ValueError: If a file cannot be parsed
    """
    graph = Graph()
    _parse_into(graph, owl_file, rdf_format)
    if ttl_file:
        _parse_into(graph, ttl_file, rdf_format)
    return graph


class OntologyGraphTransformer:
    """Writes RDF graphs into an ArangoDB database using arango-rdf."""

    def __init__(self, db: StandardDatabase):
        self.db = db
        self.arango_rdf_adapter = ArangoRDF(db)

    @classmethod
    def connect(
        cls,
        endpoint: str,
        username: str,
        password: str,
        database: str,
        create_database: bool = True,
    ) -> "OntologyGraphTransformer":
        """
        Connect to a database, creating it if it does not exist.

        The target database is checked first, so users without access to
        ``_system`` (common on managed deployments) can use existing databases.
        """
        client = ArangoClient(hosts=endpoint)
        db = client.db(database, username=username, password=password)
        try:
            db.properties()
        except DatabasePropertiesError as e:
            if e.http_code == 401:
                # ArangoDB also answers 401 when a non-admin user asks for a missing database
                raise PermissionError(
                    f"Not authorized for database '{database}' at {endpoint} as '{username}'. "
                    "Check the password, and that the database exists and the user can access it."
                ) from e
            if e.error_code != _ERROR_DATABASE_NOT_FOUND or not create_database:
                raise
            logger.info("Creating database %s", database)
            sys_db = client.db("_system", username=username, password=password)
            sys_db.create_database(database)
        return cls(db)

    @classmethod
    def from_cluster(
        cls,
        credential_manager: ArangoCredentialManager,
        cluster_id: str,
        database: str | None = None,
    ) -> "OntologyGraphTransformer":
        """Connect using a cluster from the .arango configuration."""
        params = credential_manager.get_connection_params(cluster_id)
        return cls.connect(
            endpoint=params["endpoint"],
            username=params["username"],
            password=params["password"],
            database=database or params["database"],
        )

    def transform(
        self,
        graph: Graph,
        pattern: str,
        graph_name: str | None = None,
        overwrite: bool = False,
    ) -> ArangoGraph:
        """
        Apply one transformation pattern.

        Args:
            graph: RDF graph to import
            pattern: One of ``PATTERNS`` (rpt, pgt, lpgt)
            graph_name: ArangoDB graph name (default: ``<pattern>_ontology_graph``)
            overwrite: Drop the existing graph and its collections first. Without it,
                re-running the same import updates documents in place.

        Returns:
            The ArangoDB graph that was written
        """
        if pattern not in PATTERNS:
            raise ValueError(f"Unknown pattern '{pattern}'. Choose from: {sorted(PATTERNS)}")

        _, method_name = PATTERNS[pattern]
        method = getattr(self.arango_rdf_adapter, method_name)
        return method(
            name=graph_name or f"{pattern}_ontology_graph",
            rdf_graph=graph,
            overwrite_graph=overwrite,
        )
