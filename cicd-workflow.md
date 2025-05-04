# PyPI Release Workflow using GitHub Actions

This document describes the automated release flow for **cloudisense-core** using GitHub Actions and a shell script (`buildnupload.sh`) to build and publish the package to **PyPI**.

---

## Overview

Whenever a version **tag** (like `v1.3.0`) is pushed to GitHub, the workflow:

1. **Triggers GitHub Actions**
2. **Builds** the Python package
3. **Validates** the distribution
4. **Uploads** the package to PyPI using your `PYPI_TOKEN` stored in GitHub Secrets

---

## Files & Structure

```bash
cloudisense-core/
├── setup.py
├── buildnupload.sh           # Custom build+upload script
└── .github/
    └── workflows/
        └── publish-pypi.yml  # GitHub Actions workflow
```

---

## Workflow Trigger

```yaml
on:
  push:
    tags:
      - 'v*'   # Triggers on tags like v1.3.0
```

---

## What the Workflow Does

1. **Checkout code**
2. **Set up Python 3.9**
3. **Run `buildnupload.sh`**, which:
   - Installs required build tools
   - Extracts version from `setup.py`
   - Builds sdist and wheel using `python3 -m build`
   - Runs `twine check`
   - Uploads to PyPI using:

     ```bash
     twine upload --repository pypi dist/*
     ```

4. **Credentials** are pulled from GitHub Secrets:
   ```yaml
   TWINE_USERNAME: __token__
   TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
   ```

---

## Prerequisites

1. A **PyPI API token** created at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. A GitHub **repository secret**:
   - Name: `PYPI_TOKEN`
   - Value: your PyPI API token (starts with `pypi-...`)

---

## How to Trigger the Release

```bash
# Ensure version is bumped in setup.py (__version__ = "1.3.0")
git add setup.py
git commit -m "Bump version to 1.3.0"
git push

# Tag and push
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0
```

This will automatically trigger the GitHub Actions workflow and publish your package to PyPI.

---

## Last Updated

2025-05-04
