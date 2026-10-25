# Working in FiberFusing

Read README.rst and CONTRIBUTING.md. Inspect git status and preserve existing
edits. Support Python 3.10+. Use an existing suitable virtual environment.
Keep maintenance changes separate from geometry and optimization changes.

Run focused tests, Ruff, and git diff --check. Packaging changes also require
building wheel and sdist, checking the installed YAML catalog outside checkout,
and running make release-check. Documentation changes require a headless Sphinx
build; gallery examples execute by default.

Version metadata is explicit and maintained by martinpdes-maintenance. Makefiles
call the installed module directly. Do not add local release scripts or SCM
versioning. Tests of commits/tags/pushes must use temporary repositories.
Create real release tags or publish packages only for an explicit release task.
