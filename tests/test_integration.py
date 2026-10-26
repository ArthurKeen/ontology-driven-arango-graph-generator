"""End-to-end transformations against a live ArangoDB.

Run with, for example:

    docker compose up -d
    ARANGO_TEST_ENDPOINT=http://localhost:8529 ARANGO_TEST_PASSWORD=change-me pytest -m integration
"""

import os
import uuid
from pathlib import Path

import pytest

from ontology_graph_generator import cli
from ontology_graph_generator.arango_credentials import wait_for_endpoint

ENDPOINT = os.environ.get("ARANGO_TEST_ENDPOINT")
PASSWORD = os.environ.get("ARANGO_TEST_PASSWORD", "")
EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not ENDPOINT, reason="ARANGO_TEST_ENDPOINT is not set"),
]


@pytest.fixture
def database(monkeypatch):
    from arango import ArangoClient

    assert wait_for_endpoint(ENDPOINT, timeout=120), f"{ENDPOINT} is not responding"
    monkeypatch.setenv(cli.PASSWORD_ENV_VAR, PASSWORD)

    name = f"odagg_test_{uuid.uuid4().hex[:8]}"
    sys_db = ArangoClient(hosts=ENDPOINT).db("_system", username="root", password=PASSWORD)
    yield ArangoClient(hosts=ENDPOINT).db(name, username="root", password=PASSWORD)
    sys_db.delete_database(name, ignore_missing=True)


def run(database, *extra):
    return cli.main(
        [
            "--endpoint",
            ENDPOINT,
            "--database",
            database.name,
            "--owl",
            str(EXAMPLES / "ontology.owl"),
            "--ttl",
            str(EXAMPLES / "sample_data.ttl"),
            "--patterns",
            "rpt",
            "pgt",
            "lpgt",
            *extra,
        ]
    )


def document_counts(database):
    return {
        collection["name"]: database.collection(collection["name"]).count()
        for collection in database.collections()
        if not collection["system"]
    }


def test_all_patterns_create_graphs_and_reruns_are_idempotent(database):
    assert run(database) == 0

    assert {graph["name"] for graph in database.graphs()} == {
        "rpt_ontology_graph",
        "pgt_ontology_graph",
        "lpgt_ontology_graph",
    }
    counts = document_counts(database)
    assert counts["worksFor"] == 1
    assert counts["Employee"] == 1

    assert run(database) == 0
    assert document_counts(database) == counts

    assert run(database, "--overwrite") == 0
    assert document_counts(database) == counts
