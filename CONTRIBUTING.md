# Contributing to FiberFusing

Use Python 3.10 or newer and an existing suitable virtual environment.

```sh
python -m pip install -e ".[testing,dev,documentation,release]"
make quality PYTHON=python
make test PYTHON=python
make docs PYTHON=python
make package-check PYTHON=python
make release-check PYTHON=python
```

The package is pure Python. Builds include the YAML fiber catalog explicitly;
validate installed wheels outside the source checkout when changing packaging.
Keep numerical changes separate from maintenance changes. Add deterministic
regressions for scientific behavior; plots alone do not establish correctness.

Documentation uses MartinPdeS-docs with the existing geometry and extra example
sections. `make docs` runs Sphinx-Gallery examples headlessly and treats Sphinx
warnings as errors. Generated gallery pages, caches, and builds are ignored.

## Releases

The explicit project version, tracked `FiberFusing/_version.py`, and
`conda.recipe/meta.yaml` are aligned by the installed martinpdes-maintenance tool.
There are no local release scripts and no Git-derived build versions.

```sh
python -m pip install "martinpdes-maintenance==0.2.2"
make release-check PYTHON=python
python -m martinpdes_maintenance.cli tag vX.Y.Z --dry-run
```

From a clean full checkout, `make tag VERSION=vX.Y.Z` updates metadata, commits,
and creates an annotated tag without pushing. `make release patch`, `minor`,
or `major` selects the next version and pushes that commit and exact tag.
Fetch remote tags before selecting a release version. A pushed `v*` tag triggers
MPSActions to build, verify, and publish PyPI and Conda packages and documentation.
The repository needs PYPI_API_TOKEN and ANACONDA_API_TOKEN secrets configured.
Normal branch pushes and pull requests test and build without publishing.

When changing workflows, compare their input names to the MPSActions interfaces.
Preserve user work, package data, and established scientific APIs. Do not run
release commands in the real repository as validation.
