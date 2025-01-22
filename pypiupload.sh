#!/bin/bash


# target destination
#repository="testpypi"
repository="testpypi"

# Path to version.py
VERSION_FILE="setup.py"

# Extract the version using grep and awk
version=$(grep "__version__" "$VERSION_FILE" | awk -F"'" '{print $2}')

# Check if version is extracted
if [ -z "$version" ]; then
  echo "Error: Could not find version variable in setup.py"
  exit 1
fi

# clear old files
rm -rf ./cdscore.egg-info
rm -rf ./build
rm -rf ./dist

# Construct the archive filename
archive_name="dist/cdscore-${version}.tar.gz"

# Build the archive
python setup.py sdist bdist_wheel

# check package
# Check the package using twine check
# twine check "$archive_name"
twine check dist/*

if [ $? -ne 0 ]; then
  echo "Package check failed. Please fix the issues and try again."
  exit 1
fi


# Check if the archive file exists
if [ ! -f "$archive_name" ]; then
  echo "Error: Archive file '$archive_name' does not exist."
  exit 1
fi

# Upload the archive with verbose output
twine upload --repository "$repository" --verbose "$archive_name"

# Check the return code of twine
if [ $? -eq 0 ]; then
  echo "Successfully uploaded archive '$archive_name' to '$repository'."
else
  echo "Error uploading archive. Please check the output for details."
fi