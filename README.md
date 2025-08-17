# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| FiberFusing/background.py                          |       23 |        2 |        0 |        0 |     91% |    52, 77 |
| FiberFusing/connection/connection.py               |      179 |       20 |       28 |        7 |     83% |76, 92, 96-98, 102-107, 169, 226, 238, 287, 319-322, 386->exit, 390, 444, 457 |
| FiberFusing/connection/connection\_optimization.py |       75 |        2 |       14 |        2 |     96% |69->71, 203-204 |
| FiberFusing/connection/utils.py                    |        8 |        0 |        0 |        0 |    100% |           |
| FiberFusing/coordinate\_system.py                  |      309 |       66 |       78 |       11 |     74% |75, 82->86, 92->96, 112, 114, 256, 270, 438-445, 471, 522-525, 649, 693, 759, 775-781, 792-798, 809-815, 833-844, 890-895, 901-903, 909-911, 917-919, 925-927, 950 |
| FiberFusing/fiber/generic\_fiber.py                |      151 |       41 |       42 |        7 |     70% |40, 49, 59, 76, 88-99, 170, 176, 224, 255->254, 272-273, 337-339, 408, 412->418, 415-416, 453-479, 497-498, 583, 601-605 |
| FiberFusing/fiber/loader.py                        |       76 |       16 |       24 |        6 |     74% |39, 63, 70, 94-98, 159->162, 205, 229-230, 268, 289, 311-316 |
| FiberFusing/geometries/base\_class.py              |      111 |       10 |        6 |        3 |     89% |55, 67, 190, 202, 238, 320-322, 343, 409->411, 436 |
| FiberFusing/geometries/linestring.py               |       69 |        6 |        6 |        2 |     89% |26, 32, 44, 59, 78-79 |
| FiberFusing/geometries/point.py                    |       42 |        5 |        2 |        1 |     86% |27, 45-46, 67, 73 |
| FiberFusing/geometries/polygon.py                  |       76 |        7 |       26 |        5 |     84% |74, 83, 106-107, 111, 180-181 |
| FiberFusing/geometries/utils.py                    |       23 |        1 |       12 |        2 |     91% |51->46, 57 |
| FiberFusing/geometry.py                            |      186 |       36 |       72 |       18 |     74% |81, 88-90, 96-98, 124-130, 138, 140, 142, 151, 153, 155, 160->exit, 163->166, 168->exit, 180-183, 194-197, 212, 229, 241, 252, 277-282, 320, 325, 420->424, 424->428, 428->431 |
| FiberFusing/helper.py                              |       31 |        1 |       10 |        1 |     95% |        49 |
| FiberFusing/optical\_structure.py                  |       29 |        6 |        0 |        0 |     79% |64, 82-84, 95-96 |
| FiberFusing/plottings.py                           |       21 |        1 |        8 |        1 |     93% |        40 |
| FiberFusing/profile.py                             |      159 |       31 |       50 |        9 |     77% |71, 83, 87-103, 129, 179-185, 201, 217, 248->251, 264, 319-320, 339, 343, 354, 370, 476->479, 479->482, 482->485, 485->489, 490-491 |
| FiberFusing/shapes/base.py                         |        2 |        0 |        0 |        0 |    100% |           |
| FiberFusing/shapes/circle.py                       |       18 |        1 |        2 |        1 |     90% |        45 |
| FiberFusing/shapes/ellipse.py                      |       23 |        9 |        4 |        0 |     52% |     46-68 |
| FiberFusing/shapes/square.py                       |       18 |        6 |        2 |        0 |     60% |     39-53 |
| FiberFusing/structures.py                          |       73 |        1 |        6 |        0 |     99% |        50 |
| FiberFusing/utils.py                               |       32 |        6 |        6 |        2 |     79% |57, 79, 100-101, 118-120 |
|                                          **TOTAL** | **1734** |  **274** |  **398** |   **78** | **80%** |           |


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