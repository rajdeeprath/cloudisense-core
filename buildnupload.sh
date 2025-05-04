#!/bin/bash

set -e  # Exit script immediately on any command error
set -o pipefail  # Exit if any command in a pipeline fails

# Function to install twine if missing
function ensure_twine_installed {
    if ! command -v twine &> /dev/null; then
        echo "⚠️  Twine not found. Installing..."
        if command -v pip &> /dev/null; then
            pip install --upgrade twine
        elif command -v pip3 &> /dev/null; then
            pip3 install --upgrade twine
        else
            echo "❌ ERROR: Neither pip nor pip3 found. Please install Python and pip."
            exit 1
        fi
    else
        echo "✅ Twine is installed."
    fi
}


# Function to ensure necessary packages are updated
function ensure_latest_tools {
    echo "🔄 Updating packaging tools (setuptools, wheel, twine, pkginfo)..."
    if command -v pip &> /dev/null; then
        pip install --upgrade setuptools wheel twine pkginfo build
    elif command -v pip3 &> /dev/null; then
        pip3 install --upgrade setuptools wheel twine pkginfo build
    else
        echo "❌ ERROR: Neither pip nor pip3 found. Please install Python and pip."
        exit 1
    fi
}

# Ensure required tools are installed and updated
ensure_latest_tools

# Target repository (change to testpypi if needed)
repository="testpypi"
# repository="pypi"

# Path to setup.py
VERSION_FILE="setup.py"

install="true"

# Function to print error and exit
function error_exit {
    echo "❌ ERROR: $1"
    exit 1
}

# Extract version from setup.py
echo "📦 Extracting package version..."
version=$(grep -Eo '__version__ *= *["'"'"'][0-9]+\.[0-9]+\.[0-9]+["'"'"']' $VERSION_FILE | sed -E 's/__version__ *= *["'"'"']([0-9]+\.[0-9]+\.[0-9]+)["'"'"']/\1/')

# Check if version was extracted
if [ -z "$version" ]; then
    error_exit "Could not determine version from $VERSION_FILE. Ensure '__version__' is defined properly."
fi

echo "✅ Version detected: $version"

# Clear old build artifacts
echo "🧹 Cleaning old build files..."
rm -rf ./cdscore.egg-info ./build ./dist

# Construct the expected archive name
archive_name="dist/cdscore-${version}.tar.gz"

# Build the package
echo "⚙️ Building the package..."
python setup.py sdist bdist_wheel

# Verify package integrity
ensure_twine_installed
echo "🔍 Checking package integrity with twine..."
twine check dist/* || error_exit "Package check failed. Please fix the issues and try again."

# Ensure the archive file exists
if [ ! -f "$archive_name" ]; then
    error_exit "Build failed: Expected archive file '$archive_name' not found in dist/."
fi

echo "Build successful: $archive_name"


if [ "$install" == "true" ]; then
    echo "Installing locally..."
    pip install -e .    
else
    # Upload to PyPI (or testpypi)
    echo "🚀 Uploading package to $repository..."
    twine upload --repository "$repository" --verbose dist/* || error_exit "Upload failed. Please check the logs for details."
    echo "🎉 Successfully uploaded archive '$archive_name' to '$repository'."
fi