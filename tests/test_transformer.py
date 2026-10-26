from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rdflib import Graph

from ontology_graph_generator.transformer import PATTERNS, OntologyGraphTransformer, load_ontology

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_loads_rdf_xml_ontology_and_turtle_data():
    graph = load_ontology(str(EXAMPLES / "ontology.owl"), str(EXAMPLES / "sample_data.ttl"))

    ontology_only = load_ontology(str(EXAMPLES / "ontology.owl"))
    assert len(graph) > len(ontology_only) > 0


def test_loads_turtle_saved_with_owl_extension(tmp_path):
    turtle_as_owl = tmp_path / "ontology.owl"
    Graph().parse(EXAMPLES / "ontology.owl").serialize(turtle_as_owl, format="turtle")

    assert len(load_ontology(str(turtle_as_owl))) == len(
        load_ontology(str(EXAMPLES / "ontology.owl"))
    )


def test_missing_files_raise_instead_of_being_skipped(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing.owl"):
        load_ontology(str(tmp_path / "missing.owl"))

    with pytest.raises(FileNotFoundError, match="missing.ttl"):
        load_ontology(str(EXAMPLES / "ontology.owl"), str(tmp_path / "missing.ttl"))


def test_unparseable_file_raises_value_error(tmp_path):
    broken = tmp_path / "broken.owl"
    broken.write_text("this is not RDF in any format {", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not parse"):
        load_ontology(str(broken))


def make_transformer():
    transformer = OntologyGraphTransformer.__new__(OntologyGraphTransformer)
    transformer.db = MagicMock()
    transformer.arango_rdf_adapter = MagicMock()
    return transformer


@pytest.mark.parametrize("pattern", sorted(PATTERNS))
def test_transform_calls_matching_arango_rdf_method(pattern):
    transformer = make_transformer()
    graph = Graph()

    transformer.transform(graph, pattern)

    method = getattr(transformer.arango_rdf_adapter, PATTERNS[pattern][1])
    method.assert_called_once_with(
        name=f"{pattern}_ontology_graph", rdf_graph=graph, overwrite_graph=False
    )


def test_transform_passes_graph_name_and_overwrite():
    transformer = make_transformer()

    transformer.transform(Graph(), "pgt", graph_name="custom", overwrite=True)

    transformer.arango_rdf_adapter.rdf_to_arangodb_by_pgt.assert_called_once()
    kwargs = transformer.arango_rdf_adapter.rdf_to_arangodb_by_pgt.call_args.kwargs
    assert kwargs["name"] == "custom"
    assert kwargs["overwrite_graph"] is True


def test_transform_rejects_unknown_pattern():
    with pytest.raises(ValueError, match="Unknown pattern"):
        make_transformer().transform(Graph(), "nope")
