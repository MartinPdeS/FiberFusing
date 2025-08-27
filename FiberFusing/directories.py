#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import FiberFusing


__all__ = [
    'root_path',
    'project_path',
    'doc_path',
    'doc_css_path',
]

root_path = Path(FiberFusing.__path__[0])

project_path = root_path.parents[0]

example_directory = root_path.joinpath('examples')

doc_path = project_path.joinpath('docs')

examples_path = project_path.joinpath('docs/examples')

doc_css_path = doc_path.joinpath('source/_static/default.css')


if __name__ == '__main__':
    for path_name in __all__:
        path = locals()[path_name]
        print(path)
        assert path.exists(), f"Path {path_name} do not exists"

# -
