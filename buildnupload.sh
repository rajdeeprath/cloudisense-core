#!/bin/bash

# Exit immediately on any error
set -e
# Fail if any command in a pipeline fails
set -o pipefail

# ========================
# CONFIGURATION
# ========================

# Whether to install the package locally in editable mode.
# Default: false (used in CI to upload to PyPI)
# Usage: INSTALL_LOCAL=true ./buildnupload.sh
INSTALL_LOCAL="${INSTALL_LOCAL:-false}"

# PyPI repository to upload to: 'pypi' or 'testpypi'
# Usage: PYPI_REPO=testpypi ./buildnupload.sh
PYPI_REPO="${PYPI_REPO:-pypi}"

# ========================
# FUNCTIONS
# ========================

# Ensure all required Python build and publishing tools are installed
function ensure_tools {
    echo "🔧 Installing/updating Python build tools..."
    python3 -m pip install --upgrade pip
    pip install --upgrade setuptools wheel twine build pkginfo
}

# Extract the __version__ string from setup.py
function extract_version {
    VERSION_FILE="setup.py"
    echo "📦 Extracting package version from $VERSION_FILE..."

    version=$(grep -Eo '__version__ *= *["'"'"'][0-9]+\.[0-9]+\.[0-9]+["'"'"']' "$VERSION_FILE" | \
              sed -E 's/__version__ *= *["'"'"']([0-9]+\.[0-9]+\.[0-9]+)["'"'"']/\1/')

    if [ -z "$version" ]; then
        echo "❌ ERROR: Version not found in $VERSION_FILE"
        exit 1
    fi

    echo "✅ Detected version: $version"
}

# Clean up previous build artifacts
function clean_artifacts {
    echo "🧹 Removing old build artifacts..."
    rm -rf dist/ build/ *.egg-info
}

# Build source distribution and wheel
function build_package {
    echo "⚙️ Building the package..."
    python3 -m build
}

# Validate the built package with twine
function check_package {
    echo "🔍 Checking package integrity with twine..."
    twine check dist/*
}

# Upload the built package to PyPI or TestPyPI
function upload_package {
    echo "🚀 Uploading to $PYPI_REPO..."
    twine upload --repository "$PYPI_REPO" dist/*
}

# Install the package locally in editable mode
function install_local {
    echo "📦 Installing locally in editable mode..."
    pip install -e .
}

# ========================
# MAIN EXECUTION
# ========================

# Step 1: Setup environment
ensure_tools

# Step 2: Read the version from setup.py
extract_version

# Step 3: Clean up old builds
clean_artifacts

# Step 4: Build the package
build_package

# Step 5: Validate the build
check_package

# Step 6: Either install locally or upload
if [ "$INSTALL_LOCAL" == "true" ]; then
    install_local
else
    upload_package
fi

echo "🎉 Done. Version $version processed successfully."
