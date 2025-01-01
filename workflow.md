# Development Workflow


## How to Use This

`cdscore` is a core dependency of Cloudisense. It must be installed into the virtual environment before Cloudisense can be run. It is also required when building a module for Cloudisense.

---

### Installing Locally

You can install this library locally without uploading it to the PyPI repository by running the following command:

```sh
python setup.py install
```

Make sure to install it into the same virtual environment that Cloudisense uses. This ensures you can run Cloudisense against it and test it before committing to PyPI.

---

### Committing to PyPI

To properly use `cdscore` in Cloudisense or a module project, it must be published to the global Python repository, PyPI. Follow these steps:

#### 1. Bump the Version
Update the version number mentioned in `setup.py` under `__version__`.

#### 2. Configure for Test PyPI
In the file `pypiupload.sh`, modify the line:
```sh
repository="pypi"
```
to:
```sh
repository="testpypi"
```

#### 3. Upload to Test PyPI
Run the shell script `pypiupload.sh` to upload the library files to [Test PyPI](https://test.pypi.org/). 

#### 4. Install from Test PyPI
Once uploaded, manually install the library into Cloudisense from Test PyPI:

```sh
pip install -i https://test.pypi.org/simple/ cdscore
```

#### 5. Commit to PyPI
After thoroughly testing, commit the library to the actual PyPI repository:
1. Update the line in `pypiupload.sh` back to:
   ```sh
   repository="pypi"
   ```
2. Run the shell script `pypiupload.sh` to upload the library files to [PyPI](https://pypi.org/).

---

### Adding to Cloudisense

Once published on PyPI, add `cdscore` as a dependency in the `requirements` file for Cloudisense. You can specify it simply as:

```
cdscore
```

Or with a specific version:

```
cdscore==<version>
```

Replace `<version>` with the version number you committed.
