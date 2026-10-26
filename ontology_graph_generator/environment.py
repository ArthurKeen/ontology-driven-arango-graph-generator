"""
Environment check for ontology-to-ArangoDB transformations.

Validates the Python version, required packages, Docker, and the local .arango file.
Install dependencies with ``pip install -e .`` rather than from this tool.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)

REQUIRED_MODULES = [
    ("yaml", "PyYAML"),
    ("rdflib", "rdflib"),
    ("arango", "python-arango"),
    ("arango_rdf", "arango-rdf"),
]


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < MIN_PYTHON:
        print(f"❌ Python {'.'.join(map(str, MIN_PYTHON))} or higher is required.")
        print(f"   Current version: {sys.version.split()[0]}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_module_installed(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None


def check_dependencies():
    """Check that every required package can be imported."""
    all_installed = True
    for module, package in REQUIRED_MODULES:
        if check_module_installed(module):
            print(f"✅ {package}")
        else:
            print(f"❌ {package} (missing)")
            all_installed = False
    if not all_installed:
        print('   Install with: python -m pip install -e ".[dev]"')
    return all_installed


def check_docker_available():
    """Check if Docker is available and running. Docker is optional, so this never fails."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Docker available: {result.stdout.strip()}")
        subprocess.run(["docker", "info"], capture_output=True, text=True, check=True)
        print("✅ Docker daemon is running")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not available or not running (only needed for local Docker clusters)")
    return True


def check_arango_config(config_path):
    """Check that the .arango configuration file exists and is valid."""
    from .arango_credentials import ArangoCredentialManager

    if not Path(config_path).exists():
        print(f"⚠️  {config_path} not found")
        print("   Copy .arango.example to .arango, or use --endpoint for direct connections")
        return True

    try:
        manager = ArangoCredentialManager(config_path)
    except ValueError as e:
        print(f"❌ {config_path} is invalid: {e}")
        return False
    print(f"✅ {config_path} is valid ({len(manager.list_clusters())} cluster(s))")
    return True


def main(argv=None):
    """Run all environment checks."""
    parser = argparse.ArgumentParser(
        prog="ontology-env", description="Check the environment for ontology transformations"
    )
    parser.add_argument(
        "--config", default=".arango", help="Path to ArangoDB configuration file (default: .arango)"
    )
    args = parser.parse_args(argv)

    print("🔍 Validating Environment...")
    print("=" * 50)

    results = [check_python_version()]
    print("\n📋 Dependencies:")
    results.append(check_dependencies())
    print("\n📋 Services and configuration:")
    results.append(check_docker_available())
    if check_module_installed("yaml"):
        results.append(check_arango_config(args.config))

    if all(results):
        print("\n🎉 Environment looks good!")
        print("\n📋 Next Steps:")
        print("   1. List clusters: ontology-transform --list-clusters")
        print("   2. Test connection: ontology-transform --cluster <name> --test-connection")
        print("   3. Transform: ontology-transform --cluster <name> --owl examples/ontology.owl")
        return 0

    print("\n⚠️  Environment validation failed. See the messages above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
