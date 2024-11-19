#!/bin/bash

# Extract version number from setup.py
version_line=$(grep -E "^__version__ = ['\"](.+)['\"]$" setup.py | cut -d "'" -f2)
version=$(echo "$version_line" | sed -E 's/^__version__ = "([^"]+)"$/\1/')


# Check if version is extracted
if [ -z "$version" ]; then
  echo "Error: Could not find version variable in setup.py"
  exit 1
fi

# Construct the archive filename
archive_name="dist/mekanixe-core-${version}.tar.gz"

# Build the archive
python setup.py sdist bdist_wheel

# check package
# Check the package using twine check
twine check "$archive_name"
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
twine upload --repository testpypi --verbose "$archive_name"

# Check the return code of twine
if [ $? -eq 0 ]; then
  echo "Successfully uploaded archive '$archive_name' to test PyPI."
else
  echo "Error uploading archive. Please check the output for details."
fi