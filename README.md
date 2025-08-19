# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| FiberFusing/background.py                          |       23 |        2 |        0 |        0 |     91% |    52, 77 |
| FiberFusing/connection/connection.py               |      179 |       20 |       28 |        7 |     83% |76, 92, 96-98, 102-107, 169, 226, 238, 287, 319-322, 386->exit, 390, 444, 457 |
| FiberFusing/connection/connection\_optimization.py |       75 |        2 |       14 |        2 |     96% |69->71, 203-204 |
| FiberFusing/connection/utils.py                    |        8 |        0 |        0 |        0 |    100% |           |
| FiberFusing/coordinate\_system.py                  |      245 |       18 |       60 |       10 |     89% |80->84, 90->94, 110, 112, 254, 268, 436-443, 469, 520-523, 647, 691, 791 |
| FiberFusing/fiber/generic\_fiber.py                |      151 |       43 |       44 |        7 |     68% |40, 55-56, 61, 71, 88, 100-111, 156, 162, 210, 240->239, 257-258, 322-324, 393, 397->403, 400-401, 436-462, 480-481, 566, 584-588 |
| FiberFusing/fiber/loader.py                        |       66 |       10 |       22 |        6 |     80% |39, 63, 70, 94-98, 159->162, 205, 229-230 |
| FiberFusing/geometries/base\_class.py              |       42 |        2 |        0 |        0 |     95% |    52, 64 |
| FiberFusing/geometries/linestring.py               |       68 |        6 |        6 |        2 |     89% |25, 31, 43, 66, 106-107 |
| FiberFusing/geometries/point.py                    |       40 |        5 |        2 |        1 |     86% |25, 53-54, 85, 91 |
| FiberFusing/geometries/polygon.py                  |      140 |       15 |       32 |        8 |     84% |73, 82, 105-106, 110, 179-180, 230, 242, 278, 360-362, 383, 449->451, 476 |
| FiberFusing/geometries/utils.py                    |       22 |        1 |       12 |        2 |     91% |51->46, 57 |
| FiberFusing/geometry.py                            |      189 |       36 |       74 |       18 |     75% |81, 88-90, 96-98, 124-130, 138, 140, 142, 151, 153, 155, 160->exit, 163->166, 168->exit, 180-183, 194-197, 212, 229, 241, 252, 277-282, 320, 325, 425->429, 429->433, 433->436 |
| FiberFusing/graded\_index.py                       |        5 |        0 |        0 |        0 |    100% |           |
| FiberFusing/helper.py                              |       31 |        1 |       10 |        1 |     95% |        49 |
| FiberFusing/optical\_structure.py                  |       26 |        6 |        0 |        0 |     77% |57, 75-77, 88-89 |
| FiberFusing/plottings.py                           |       21 |        1 |        8 |        1 |     93% |        40 |
| FiberFusing/profile.py                             |      160 |       31 |       52 |        7 |     78% |71, 83, 87-103, 129, 179-185, 201, 217, 245->248, 261, 313-314, 332, 336, 347, 363, 470->473, 483->487, 488-489 |
| FiberFusing/shapes/base.py                         |        2 |        0 |        0 |        0 |    100% |           |
| FiberFusing/shapes/circle.py                       |       18 |        1 |        2 |        1 |     90% |        45 |
| FiberFusing/shapes/ellipse.py                      |       22 |        9 |        4 |        0 |     50% |     45-67 |
| FiberFusing/shapes/square.py                       |       18 |        6 |        2 |        0 |     60% |     39-53 |
| FiberFusing/structures.py                          |       69 |        2 |        8 |        1 |     96% |   50, 221 |
| FiberFusing/utils.py                               |       32 |        6 |        6 |        2 |     79% |57, 79, 100-101, 118-120 |
|                                          **TOTAL** | **1652** |  **223** |  **386** |   **76** | **82%** |           |


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