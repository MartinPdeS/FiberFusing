# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| FiberFusing/background.py                          |       21 |        2 |        0 |        0 |     90.48% |    51, 76 |
| FiberFusing/connection/connection.py               |      179 |       20 |       28 |        7 |     83.09% |76, 92, 96-98, 102-107, 169, 226, 238, 287, 319-322, 386->exit, 390, 444, 457 |
| FiberFusing/connection/connection\_optimization.py |       75 |        2 |       14 |        2 |     95.51% |69->71, 203-204 |
| FiberFusing/coordinate\_system.py                  |      246 |       18 |       60 |       10 |     88.89% |82->86, 92->96, 112, 114, 256, 270, 438-445, 471, 522-525, 649, 693, 793 |
| FiberFusing/fiber/generic\_fiber.py                |      150 |       42 |       44 |        7 |     68.56% |40, 55-56, 61, 71, 88, 100-111, 156, 162, 210, 240->239, 257-258, 322-324, 393, 397->403, 400-401, 436-462, 480-481, 566, 584-592 |
| FiberFusing/fiber/loader.py                        |       66 |        5 |       22 |        5 |     88.64% |39, 63, 159->162, 205, 229-230 |
| FiberFusing/geometries/base\_class.py              |       42 |        2 |        0 |        0 |     95.24% |    52, 64 |
| FiberFusing/geometries/linestring.py               |       69 |        6 |        6 |        2 |     89.33% |26, 32, 44, 67, 107-108 |
| FiberFusing/geometries/point.py                    |       41 |        5 |        2 |        1 |     86.05% |26, 54-55, 86, 92 |
| FiberFusing/geometries/polygon.py                  |      140 |       15 |       32 |        8 |     84.30% |73, 82, 105-106, 110, 179-180, 230, 242, 278, 360-362, 383, 449->451, 476 |
| FiberFusing/geometries/utils.py                    |       22 |        1 |       12 |        2 |     91.18% |51->46, 57 |
| FiberFusing/geometry.py                            |      178 |       36 |       68 |       15 |     74.39% |85, 92-94, 100-102, 133-144, 154, 156, 158, 169, 171, 173, 178->exit, 183->186, 190->exit, 202-205, 216-219, 238, 257, 273, 289, 314-324, 364, 371 |
| FiberFusing/helper.py                              |       13 |        1 |        4 |        1 |     88.24% |        21 |
| FiberFusing/optical\_structure.py                  |       23 |        6 |        0 |        0 |     73.91% |59, 77-79, 90-91 |
| FiberFusing/plottings.py                           |       21 |        1 |        8 |        1 |     93.10% |        40 |
| FiberFusing/profile.py                             |      161 |       31 |       52 |        7 |     78.40% |73, 85, 89-105, 131, 181-187, 203, 219, 247->250, 263, 315-316, 334, 338, 349, 365, 472->475, 485->489, 490-491 |
| FiberFusing/shapes/circle.py                       |       16 |        1 |        2 |        1 |     88.89% |        45 |
| FiberFusing/shapes/ellipse.py                      |       20 |        9 |        4 |        0 |     45.83% |     45-67 |
| FiberFusing/shapes/square.py                       |       16 |        6 |        2 |        0 |     55.56% |     39-53 |
| FiberFusing/structures.py                          |       65 |        2 |        8 |        1 |     95.89% |   52, 223 |
| FiberFusing/utils.py                               |       34 |        6 |        6 |        2 |     80.00% |68, 90, 111-112, 129-131 |
|                                          **TOTAL** | **1611** |  **217** |  **374** |   **72** | **82.62%** |           |

3 files skipped due to complete coverage.


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/MartinPdeS/FiberFusing/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/MartinPdeS/FiberFusing/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FMartinPdeS%2FFiberFusing%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.