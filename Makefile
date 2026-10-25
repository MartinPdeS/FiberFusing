.DEFAULT_GOAL := help
PYTHON ?= python3
DOCS_BUILD_DIR ?= docs/build/html
RELEASE_KIND := $(filter major minor patch,$(MAKECMDGOALS))
.PHONY: help editable test quality check docs build package-check release-check tag release major minor patch
help:
	@echo "FiberFusing: editable, test, quality, check, docs, build, package-check"
	@echo "Releases: release-check, tag VERSION=vX.Y.Z, release patch|minor|major"
editable:
	$(PYTHON) -m pip install -e ".[testing,dev,documentation,release]"
test:
	MPLBACKEND=Agg $(PYTHON) -m pytest
quality:
	$(PYTHON) -m ruff check FiberFusing tests
check: quality test release-check
docs:
	MPLBACKEND=Agg $(PYTHON) -m sphinx -W --keep-going -b html docs/source $(DOCS_BUILD_DIR)
build:
	$(PYTHON) -m build
package-check: build
	$(PYTHON) -m twine check dist/*
release-check:
	$(PYTHON) -m martinpdes_maintenance.cli check $(if $(VERSION),--version $(VERSION),)
tag:
	$(PYTHON) -m martinpdes_maintenance.cli tag "$(VERSION)"
release:
	@test "$(words $(RELEASE_KIND))" -eq 1 || { echo "usage: make release [patch|minor|major]" >&2; exit 2; }
	@set -eu; release_tag="$$($(PYTHON) -m martinpdes_maintenance.cli next $(RELEASE_KIND))"; \
	$(PYTHON) -m martinpdes_maintenance.cli tag "$$release_tag"; \
	git push origin HEAD "refs/tags/$$release_tag"
major minor patch:
	@:
