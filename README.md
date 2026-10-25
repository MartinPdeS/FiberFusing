# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ---------: | --------: |
| FiberFusing/background.py                          |       21 |        2 |        0 |        0 |     90.48% |    51, 76 |
| FiberFusing/connection/connection.py               |      180 |       20 |       28 |        7 |     83.17% |76, 92, 96-98, 102-107, 169, 226, 238, 287, 319-322, 387-\>exit, 391, 445, 458 |
| FiberFusing/connection/connection\_optimization.py |       89 |        2 |       20 |        3 |     95.41% |70-\>72, 213, 240 |
| FiberFusing/coordinate\_system.py                  |      246 |       18 |       60 |       10 |     88.89% |82-\>86, 92-\>96, 112, 114, 256, 270, 438-445, 471, 522-525, 649, 693, 793 |
| FiberFusing/fiber/generic\_fiber.py                |      150 |       42 |       44 |        7 |     68.56% |40, 55-56, 61, 71, 88, 100-111, 156, 162, 210, 240-\>239, 257-258, 322-324, 393, 397-\>403, 400-401, 436-462, 480-481, 566, 584-592 |
| FiberFusing/fiber/loader.py                        |       66 |        5 |       22 |        5 |     88.64% |39, 63, 159-\>162, 205, 229-230 |
| FiberFusing/geometries/base\_class.py              |       43 |        2 |        0 |        0 |     95.35% |    53, 65 |
| FiberFusing/geometries/linestring.py               |       70 |        6 |        6 |        2 |     89.47% |27, 33, 45, 68, 108-109 |
| FiberFusing/geometries/point.py                    |       42 |        5 |        2 |        1 |     86.36% |27, 55-56, 87, 93 |
| FiberFusing/geometries/polygon.py                  |      140 |       11 |       32 |        5 |     89.53% |82, 110, 179-180, 230, 242, 278, 360-362, 449-\>451, 476 |
| FiberFusing/geometries/utils.py                    |       22 |        1 |       12 |        2 |     91.18% |51-\>46, 57 |
| FiberFusing/geometry.py                            |      178 |       36 |       68 |       15 |     74.39% |85, 92-94, 100-102, 133-144, 154, 156, 158, 169, 171, 173, 178-\>exit, 183-\>186, 190-\>exit, 202-205, 216-219, 238, 257, 273, 289, 314-324, 364, 371 |
| FiberFusing/helper.py                              |       13 |        1 |        4 |        1 |     88.24% |        21 |
| FiberFusing/optical\_structure.py                  |       23 |        6 |        0 |        0 |     73.91% |59, 77-79, 90-91 |
| FiberFusing/plottings.py                           |       66 |        7 |       38 |        8 |     85.58% |49, 109, 112, 122, 124, 128, 130, 131-\>133 |
| FiberFusing/profile.py                             |      200 |       23 |       74 |       16 |     85.04% |83, 86, 93, 98, 101-106, 132, 205, 221, 249-\>252, 263, 328-329, 348, 350-\>349, 369, 397, 414, 435, 452, 507-\>510, 520-\>524, 525-526 |
| FiberFusing/shapes/circle.py                       |       21 |        1 |        6 |        1 |     92.59% |        46 |
| FiberFusing/shapes/ellipse.py                      |       25 |       13 |        8 |        0 |     36.36% |     46-72 |
| FiberFusing/shapes/square.py                       |       16 |        6 |        2 |        0 |     55.56% |     39-53 |
| FiberFusing/structures.py                          |       82 |        3 |       20 |        2 |     95.10% |40, 64, 88 |
| FiberFusing/utils.py                               |       34 |        5 |        6 |        1 |     85.00% |90, 111-112, 129-131 |
| **TOTAL**                                          | **1740** |  **215** |  **452** |   **86** | **83.90%** |           |

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