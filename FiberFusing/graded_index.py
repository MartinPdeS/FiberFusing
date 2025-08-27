from pydantic.dataclasses import dataclass

@dataclass
class GradedIndex:
    """
    Represents a graded index for a material, including its refractive index and other properties.

    Parameters
    ----------
    inside : float
        The refractive index of the material inside the fiber.
    outside : float
        The refractive index of the material outside the fiber.
    """
    inside: float
    outside: float
