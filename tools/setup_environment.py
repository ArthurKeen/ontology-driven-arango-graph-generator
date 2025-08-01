#!/usr/bin/env python3
"""
Environment Setup Tool for AWS Ontology ArangoDB Integration

Handles dependency installation, environment validation, and initial setup.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_module_installed(module_name):
    """Check if a Python module is installed."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_requirements():
    """Install requirements from requirements.txt."""
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print(f"📦 Installing requirements from {requirements_file}...")
    
    try:
        # Try regular pip first
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        # If regular pip fails, try with --break-system-packages
        if "externally-managed-environment" in e.stderr:
            print("⚠️  Externally managed environment detected. Trying with --break-system-packages...")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "--break-system-packages",
                    "-r", str(requirements_file)
                ], capture_output=True, text=True, check=True)
                
                print("✅ Requirements installed successfully (with --break-system-packages)")
                return True
                
            except subprocess.CalledProcessError as e2:
                print(f"❌ Failed to install requirements: {e2.stderr}")
                print("\n💡 Manual installation suggestions:")
                print("   1. Create a virtual environment:")
                print("      python3 -m venv venv")
                print("      source venv/bin/activate")
                print("      pip install -r requirements.txt")
                print("\n   2. Or use pipx for application installation:")
                print("      brew install pipx")
                print("      pipx install -r requirements.txt")
                return False
        else:
            print(f"❌ Failed to install requirements: {e.stderr}")
            return False

def check_docker_available():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, text=True, check=True
        )
        print(f"✅ Docker available: {result.stdout.strip()}")
        
        # Check if Docker daemon is running
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, text=True, check=True
        )
        print("✅ Docker daemon is running")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not available or not running")
        print("   Install Docker Desktop if you plan to use local Docker clusters")
        return False

def check_arango_config():
    """Check if .arango configuration file exists."""
    config_file = Path(__file__).parent.parent / ".arango"
    
    if not config_file.exists():
        print("❌ .arango configuration file not found")
        print("   Please create .arango file with your cluster configurations")
        return False
    
    print("✅ .arango configuration file found")
    return True

def validate_environment():
    """Run comprehensive environment validation."""
    print("🔍 Validating Environment...")
    print("=" * 50)
    
    checks = [
        ("Python version", check_python_version),
        ("Docker availability", check_docker_available),
        ("ArangoDB config", check_arango_config),
    ]
    
    # Core dependency checks
    core_modules = [
        ("yaml", "PyYAML"),
        ("rdflib", "rdflib"),
        ("arango", "python-arango"),
    ]
    
    # Optional dependency checks
    optional_modules = [
        ("arangordf", "arangordf"),
        ("owlready2", "owlready2"),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
    
    print(f"\n📋 Core Dependencies:")
    for module, package in core_modules:
        if check_module_installed(module):
            print(f"✅ {package}")
        else:
            print(f"❌ {package} (missing)")
            all_passed = False
    
    print(f"\n📋 Optional Dependencies:")
    for module, package in optional_modules:
        if check_module_installed(module):
            print(f"✅ {package}")
        else:
            print(f"⚠️  {package} (optional - install with pip install {package})")
    
    return all_passed

def main():
    """Main setup function."""
    print("🚀 AWS Ontology ArangoDB Environment Setup")
    print("=" * 50)
    
    # Check if we should install requirements
    if "--install-deps" in sys.argv or "--install" in sys.argv:
        if not install_requirements():
            sys.exit(1)
        print()
    
    # Validate environment
    if validate_environment():
        print("\n🎉 Environment setup complete!")
        print("\n📋 Next Steps:")
        print("   1. List clusters: python tools/demo_cluster_management.py --list-clusters")
        print("   2. Test connection: python tools/demo_cluster_management.py --cluster <cluster_name> --test-connection")
        print("   3. Start transformation: python tools/transform_ontology.py --cluster <cluster_name> --patterns pgt")
    else:
        print("\n⚠️  Environment validation failed!")
        print("   Run with --install-deps to attempt automatic dependency installation:")
        print("   python tools/setup_environment.py --install-deps")
        sys.exit(1)

if __name__ == "__main__":
    main()