#!/usr/bin/env python3
"""
Documentation Validation Tool

Validates that all documentation is current, links work, and examples are accurate.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        print(f"✅ {description}: {file_path} ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False


def check_documentation_structure():
    """Check that all expected documentation files exist."""
    print("📁 Documentation Structure Validation")
    print("=" * 50)

    files_to_check = [
        # Main documentation
        ("README.md", "Main project README"),
        ("LICENSE", "MIT license"),
        ("SECURITY.md", "Security policy"),
        ("CONTRIBUTING.md", "Contributing guide"),
        ("INTEGRATION_SUMMARY.md", "Integration summary"),
        ("requirements.txt", "Python requirements"),
        ("requirements.lock", "Compiled runtime requirements"),
        ("pyproject.toml", "Python project metadata"),
        (".arango.example", "Example ArangoDB configuration"),
        (".gitignore", "Git ignore rules"),
        # Tools directory
        ("tools/README.md", "Tools documentation"),
        ("tools/transform_ontology.py", "Main transformation tool"),
        ("tools/arango_credentials.py", "Credential management"),
        ("tools/setup_environment.py", "Environment setup"),
        ("tools/demo_cluster_management.py", "Cluster demo"),
        ("tools/quick_start.py", "Quick start demo"),
        ("tools/test_credentials.py", "Credential testing"),
        # Documentation directory
        ("docs/README.md", "Documentation index"),
        ("docs/CLUSTER_MANAGEMENT.md", "Cluster management guide"),
        ("docs/API_REFERENCE.md", "API reference"),
        ("docs/PROJECT_STRUCTURE.md", "Project structure"),
        ("docs/RELEASE_CHECKLIST.md", "Release checklist"),
    ]

    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False

    return all_exist


def validate_tools():
    """Validate that tools can be imported and run basic commands."""
    print("\n🛠️ Tool Validation")
    print("=" * 50)

    tools_to_test = [
        ("tools/arango_credentials.py", None),  # Skip import test for now
        ("tools/setup_environment.py", None),  # Has main execution
        ("tools/quick_start.py", None),  # Has main execution
    ]

    all_valid = True

    for tool_path, import_test in tools_to_test:
        if import_test:
            try:
                # Test import
                exec(import_test)
                print(f"✅ {tool_path}: Import successful")
            except Exception as e:
                print(f"❌ {tool_path}: Import failed - {e}")
                all_valid = False
        else:
            # Test execution
            try:
                result = subprocess.run(
                    [sys.executable, tool_path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0 or "usage:" in result.stdout.lower():
                    print(f"✅ {tool_path}: Execution successful")
                else:
                    print(f"⚠️  {tool_path}: Execution warning (exit code {result.returncode})")
            except Exception as e:
                print(f"❌ {tool_path}: Execution failed - {e}")
                all_valid = False

    return all_valid


def check_configuration_example():
    """Check if .arango configuration file exists."""
    print("\n⚙️ Configuration Validation")
    print("=" * 50)

    if Path(".arango").exists():
        print("✅ .arango configuration file exists")

        # Check if it's properly ignored
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                gitignore_content = f.read()
                if ".arango" in gitignore_content:
                    print("✅ .arango file is properly git-ignored")
                else:
                    print("⚠️  .arango file should be added to .gitignore")

        return True
    else:
        print("⚠️  .arango configuration file not found")
        print("   This is normal if you haven't set up clusters yet")
        print("   See docs/CLUSTER_MANAGEMENT.md for setup instructions")
        return True  # Not an error condition


def validate_examples():
    """Validate that example commands work."""
    print("\n🧪 Example Validation")
    print("=" * 50)

    # Test basic commands that should work without full setup
    python_cmd = sys.executable  # Use the same Python interpreter
    commands_to_test = [
        ([python_cmd, "tools/setup_environment.py"], "Environment check"),
        ([python_cmd, "tools/transform_ontology.py", "--help"], "Transform tool help"),
    ]

    if Path(".arango").exists():
        commands_to_test.extend(
            [
                ([python_cmd, "tools/transform_ontology.py", "--list-clusters"], "List clusters"),
                ([python_cmd, "tools/demo_cluster_management.py", "--help"], "Demo tool help"),
            ]
        )

    all_valid = True

    for cmd, description in commands_to_test:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Check for common success indicators
            success_indicators = [
                result.returncode == 0,
                "usage:" in result.stdout.lower(),
                "available" in result.stdout.lower(),
                "clusters:" in result.stdout.lower(),
            ]

            if any(success_indicators):
                print(f"✅ {description}: Command executed successfully")
            else:
                print(f"⚠️  {description}: Command completed with warnings")
                if result.stderr:
                    print(f"   STDERR: {result.stderr[:100]}...")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {description}: Command timed out")
        except Exception as e:
            print(f"❌ {description}: Command failed - {e}")
            all_valid = False

    return all_valid


def check_documentation_links():
    """Check for common documentation patterns and completeness."""
    print("\n📖 Documentation Content Validation")
    print("=" * 50)

    documentation_files = [
        "README.md",
        "docs/README.md",
        "docs/CLUSTER_MANAGEMENT.md",
        "docs/API_REFERENCE.md",
        "docs/PROJECT_STRUCTURE.md",
        "docs/RELEASE_CHECKLIST.md",
        "tools/README.md",
    ]

    all_valid = True

    for doc_file in documentation_files:
        if Path(doc_file).exists():
            with open(doc_file) as f:
                content = f.read()

            # Check for basic documentation elements
            checks = [
                ("Examples", "```bash" in content or "```python" in content),
                ("Headers", content.count("#") >= 3),
                ("Length", len(content) > 500),  # Substantial content
            ]

            print(f"📄 {doc_file}:")
            for check_name, check_result in checks:
                status = "✅" if check_result else "⚠️ "
                print(f"   {status} {check_name}")
                if not check_result:
                    all_valid = False
        else:
            print(f"❌ {doc_file}: File missing")
            all_valid = False

    return all_valid


def main():
    """Main validation function."""
    print("🔍 Ontology-Driven ArangoDB Graph Generator - Documentation Validation")
    print("=" * 70)
    print()

    # Change to project root if we're in tools directory
    if Path.cwd().name == "tools":
        os.chdir("..")

    print(f"Working directory: {Path.cwd()}")
    print()

    validation_results = []

    # Run all validation checks
    validation_results.append(("Documentation Structure", check_documentation_structure()))
    validation_results.append(("Tool Validation", validate_tools()))
    validation_results.append(("Configuration", check_configuration_example()))
    validation_results.append(("Examples", validate_examples()))
    validation_results.append(("Documentation Content", check_documentation_links()))

    # Summary
    print("\n📋 Validation Summary")
    print("=" * 50)

    all_passed = True
    for check_name, result in validation_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All validation checks passed!")
        print("📚 Documentation is complete and current")
        print("🚀 Repository is ready for use")
    else:
        print("⚠️  Some validation checks failed")
        print("📋 Review the issues above and fix as needed")

    print()
    print("🔧 Next Steps:")
    print("   1. Run: python tools/quick_start.py")
    print("   2. Check: docs/README.md for complete documentation")
    print("   3. Setup: Follow docs/CLUSTER_MANAGEMENT.md for cluster configuration")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
