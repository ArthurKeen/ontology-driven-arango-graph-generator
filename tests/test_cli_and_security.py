import subprocess
import sys

from tools.demo_cluster_management import mask_secret


def test_mask_secret_preserves_only_length():
    assert mask_secret("sample-value") == "************"
    assert mask_secret("") == ""


def test_transform_help_runs_without_configuration_file():
    result = subprocess.run(
        [sys.executable, "tools/transform_ontology.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--list-clusters" in result.stdout
    assert "--patterns" in result.stdout
