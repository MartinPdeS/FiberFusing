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

## Plotting and dependencies

Use Matplotlib directly through FiberFusing.plottings. Do not add MPSPlots or
another plotting-wrapper dependency. Keep Figure return values, supplied-axes
support, headless rendering, and explicit show=False behavior working. Preserve
existing public plotting keyword arguments. Scope style changes to a call and
close newly created figures when drawing fails; do not close caller-owned figures.

## Branding

Keep editable prompts and generated candidate assets together under branding/.
Do not replace the active logo or favicon until the user selects a candidate.
Keep the selected logo, square icon, and favicon consistent and retain their
source artifacts. Preserve transparency and test small-size legibility.
