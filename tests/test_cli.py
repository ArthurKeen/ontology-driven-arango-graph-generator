import subprocess
import sys
from pathlib import Path

import pytest

from ontology_graph_generator import cli

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
ARANGO_EXAMPLE = Path(__file__).resolve().parent.parent / ".arango.example"


def test_help_runs_as_module_without_configuration_file(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "ontology_graph_generator", "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert "--list-clusters" in result.stdout
    assert "--patterns" in result.stdout


def test_password_is_never_a_command_line_flag():
    options = {opt for action in cli.build_parser()._actions for opt in action.option_strings}

    assert "--password" not in options


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--cluster", "local_dev"],
        ["--endpoint", "http://localhost:8529", "--cluster", "local_dev", "--test-connection"],
        ["--endpoint", "http://localhost:8529", "--start-container"],
    ],
)
def test_invalid_argument_combinations_exit_with_usage_error(argv):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(argv)

    assert excinfo.value.code == 2


def test_missing_configuration_file_is_reported(tmp_path, capsys):
    exit_code = cli.main(["--config", str(tmp_path / "missing"), "--list-clusters"])

    assert exit_code == 1
    assert "--endpoint" in capsys.readouterr().err


def test_missing_ontology_fails_before_connecting(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli, "connect", lambda args: pytest.fail("should not connect"))

    exit_code = cli.main(["--endpoint", "http://localhost:1", "--owl", str(tmp_path / "x.owl")])

    assert exit_code == 1
    assert "x.owl" in capsys.readouterr().err


def test_list_clusters_from_example_config(capsys, monkeypatch):
    monkeypatch.setattr(
        "ontology_graph_generator.arango_credentials.ArangoCredentialManager.check_docker_container_status",
        lambda self, cluster_id: "running",
    )

    assert cli.main(["--config", str(ARANGO_EXAMPLE), "--list-clusters"]) == 0

    output = capsys.readouterr().out
    assert "local_dev" in output
    assert "cloud_demo" in output


def test_unknown_cluster_is_reported(capsys):
    exit_code = cli.main(
        ["--config", str(ARANGO_EXAMPLE), "--cluster", "nope", "--test-connection"]
    )

    assert exit_code == 1
    assert "--list-clusters" in capsys.readouterr().err


def test_transform_runs_each_pattern_with_graph_name(monkeypatch):
    calls = []

    class FakeTransformer:
        def transform(self, graph, pattern, graph_name, overwrite):
            calls.append((pattern, graph_name, overwrite, len(graph)))

    monkeypatch.setattr(cli, "connect", lambda args: FakeTransformer())

    exit_code = cli.main(
        [
            "--endpoint",
            "http://localhost:8529",
            "--owl",
            str(EXAMPLES / "ontology.owl"),
            "--ttl",
            str(EXAMPLES / "sample_data.ttl"),
            "--patterns",
            "rpt",
            "lpgt",
            "--graph-name",
            "org",
            "--overwrite",
        ]
    )

    assert exit_code == 0
    assert [call[:3] for call in calls] == [("rpt", "rpt_org", True), ("lpgt", "lpgt_org", True)]
    assert all(call[3] > 0 for call in calls)
