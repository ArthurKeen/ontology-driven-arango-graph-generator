#!/usr/bin/env python3
"""
Quick start guide for ontology-to-ArangoDB transformations.

Demonstrates the key capabilities of the cluster credential system.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Print the welcome banner."""
    print("🚀 Ontology ArangoDB Integration - Quick Start")
    print("=" * 60)
    print()


def print_section(title):
    """Print a section header."""
    print(f"\n📋 {title}")
    print("-" * 50)


def run_command(cmd, description):
    """Run a command and show its output."""
    print(f"\n💻 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("Output:")
    print("─" * 40)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print("─" * 40)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        print("─" * 40)
        return False


def main():
    """Main quick start demonstration."""
    parser = argparse.ArgumentParser(
        description="Demonstrate ontology-to-ArangoDB transformation workflows"
    )
    parser.parse_args()

    print_banner()

    print("This script demonstrates the key capabilities:")
    print("1. 📦 Install missing dependencies")
    print("2. 🧪 Test with your real clusters")
    print("3. 🐳 Start containers as needed")
    print()

    # Change to project root if needed
    project_root = Path(__file__).parent.parent
    print(f"Working directory: {project_root.absolute()}")

    # Section 1: Environment Setup and Dependency Installation
    print_section("1. Environment Setup & Dependency Installation")

    print("First, let's check your current environment:")
    run_command([sys.executable, "tools/setup_environment.py"], "Check environment status")

    print("\n💡 To install missing dependencies, you can run:")
    print("   python tools/setup_environment.py --install-deps")
    print("   OR")
    print("   python tools/transform_ontology.py --setup-deps")

    # Section 2: Cluster Management
    print_section("2. Cluster Management & Listing")

    run_command(
        [sys.executable, "tools/transform_ontology.py", "--list-clusters"],
        "List all available ArangoDB clusters",
    )

    # Section 3: Connection Testing
    print_section("3. Connection Testing")

    print("The system can test connections to your clusters:")

    # Test a local Docker cluster
    run_command(
        [
            sys.executable,
            "tools/transform_ontology.py",
            "--cluster",
            "local_dev",
            "--test-connection",
        ],
        "Test connection to local Docker cluster (local_dev)",
    )

    # Test a cloud cluster
    run_command(
        [
            sys.executable,
            "tools/transform_ontology.py",
            "--cluster",
            "cloud_demo",
            "--test-connection",
        ],
        "Test connection to cloud cluster (cloud_demo)",
    )

    # Section 4: Container Management
    print_section("4. Docker Container Management")

    print("For Docker-based clusters, the system can automatically manage containers:")

    run_command(
        [
            sys.executable,
            "tools/transform_ontology.py",
            "--cluster",
            "local_dev",
            "--start-container",
        ],
        "Start Docker container for local_dev cluster",
    )

    # Section 5: Transformation Examples
    print_section("5. Transformation Examples")

    print("Once dependencies are installed, you can run transformations:")
    print()
    print("💻 Example transformation commands:")
    print("   # Use default cluster with PGT pattern")
    print("   python tools/transform_ontology.py --patterns pgt")
    print()
    print("   # Use specific cluster")
    print("   python tools/transform_ontology.py --cluster local_dev --patterns pgt")
    print()
    print("   # Multiple patterns on cloud cluster")
    print("   python tools/transform_ontology.py --cluster cloud_demo --patterns pgt lpgt")
    print()

    # Show what happens without dependencies
    print("Let's see what happens when trying to transform without required dependencies:")
    run_command(
        [
            sys.executable,
            "tools/transform_ontology.py",
            "--cluster",
            "local_dev",
            "--patterns",
            "pgt",
        ],
        "Attempt transformation without arango-rdf (will show helpful error)",
    )

    # Section 6: Alternative Tools
    print_section("6. Alternative Management Tools")

    print("You also have specialized tools for specific tasks:")

    run_command(
        [sys.executable, "tools/demo_cluster_management.py", "--list-clusters"],
        "Using the dedicated cluster management demo tool",
    )

    run_command(
        [
            sys.executable,
            "tools/demo_cluster_management.py",
            "--cluster",
            "local_dev",
            "--test-connection",
        ],
        "Test connection using the demo tool",
    )

    # Section 7: Summary
    print_section("7. Summary & Next Steps")

    print("🎉 Quick Start Complete!")
    print()
    print("📋 What you've learned:")
    print("   ✅ How to check your environment and install dependencies")
    print("   ✅ How to list and manage multiple ArangoDB clusters")
    print("   ✅ How to test connections before running transformations")
    print("   ✅ How to automatically start Docker containers when needed")
    print("   ✅ How to run transformations with proper error handling")
    print()
    print("🔧 To get fully operational:")
    print("   1. Install dependencies: python tools/setup_environment.py --install-deps")
    print("   2. Verify your .arango file has correct credentials")
    print(
        "   3. Test connections: python tools/transform_ontology.py --cluster <name> --test-connection"
    )
    print(
        "   4. Run transformations: python tools/transform_ontology.py --cluster <name> --patterns pgt"
    )
    print()
    print("📚 Available cluster operations:")
    print("   --list-clusters          Show all clusters with status")
    print("   --test-connection        Test connectivity to a cluster")
    print("   --start-container        Start Docker container if needed")
    print("   --setup-deps            Install missing Python dependencies")
    print()
    print("🆘 For help: python tools/transform_ontology.py --help")


if __name__ == "__main__":
    main()
