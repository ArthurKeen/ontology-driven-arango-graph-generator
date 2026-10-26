"""Transform OWL/RDF ontologies into ArangoDB graph models."""

__version__ = "0.1.0"

# Exports are loaded lazily so `ontology-env` can report missing dependencies
# instead of failing on import.
_EXPORTS = {
    "ArangoCredentialManager": "arango_credentials",
    "OntologyGraphTransformer": "transformer",
    "PATTERNS": "transformer",
    "load_ontology": "transformer",
}

__all__ = [*_EXPORTS, "__version__"]


def __getattr__(name):
    if name in _EXPORTS:
        from importlib import import_module

        return getattr(import_module(f".{_EXPORTS[name]}", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
