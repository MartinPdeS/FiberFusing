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

## Shared Python style preferences

Apply these conventions to new and edited Python code. Leave unrelated existing code unchanged. Preserve each repository's existing public APIs and project-specific scientific or behavioral requirements.

- Use keyword-only parameters by default for new functions and methods, apart from implicit `self` and `cls`. Preserve existing public calling conventions unless an API change is part of the task.
- Use NumPy-style docstrings for classes, functions, methods, and properties. Document parameters, return values, units, array shapes, and limitations where they apply.
- Keep imports at module scope when practical. Use local imports only when needed to avoid circular dependencies or defer optional, expensive, or side-effectful imports.
- Keep all imports in one contiguous block, without blank lines between standard-library, third-party, and project imports.
- Avoid redundant self-alias imports such as `from package.module import Name as Name`; import the name directly unless the alias clarifies its meaning.
- Keep simple, single-purpose UI component calls on one line when practical, even when a text string is long. Use multiline formatting when several arguments or nested components make the call easier to read.
- Prefer descriptive variable and parameter names over abbreviations, including for local values and callback parameters.
- Avoid extracting a helper used only once unless it improves clarity or separates behavior that belongs in another layer.
- Keep callbacks focused on reading inputs, calling a service or workflow, and returning outputs. Move domain decisions and complicated data conversion into the appropriate service or workflow module.
- Write comments to explain non-obvious reasoning, scientific assumptions, or compatibility constraints; do not use them to narrate code that is already clear.
