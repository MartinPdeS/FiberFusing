#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, Optional
from enum import Enum
import yaml
import numpy as np
from pathlib import Path
from FiberFusing.fiber.generic_fiber import GenericFiber
from FiberFusing.geometries.point import Point


class LayerOrder(Enum):
    """Enumeration for layer ordering options."""
    IN_TO_OUT = "in-to-out"
    OUT_TO_IN = "out-to-in"


class FiberLoader:
    """
    A class for loading and processing fiber configurations from YAML files.

    This class provides methods to load fiber configurations, process layers,
    and create GenericFiber objects with the specified properties.
    """

    def __init__(self, fiber_directory: Optional[Path] = None):
        """
        Initialize the FiberLoader.

        Parameters
        ----------
        fiber_directory : Path, optional
            Directory containing fiber YAML files. Defaults to 'fiber_files' in the same directory.
        """
        if fiber_directory is None:
            self.fiber_directory = Path(__file__).parent / 'fiber_files'
        else:
            self.fiber_directory = fiber_directory


    def load_fiber(self, fiber_name: str, clad_refractive_index: float, position: Tuple[float, float] = (0, 0), remove_cladding: bool = False) -> GenericFiber:
        """
        Load a fiber configuration and construct a GenericFiber object based on specified parameters.

        Parameters
        ----------
        fiber_name : str
            The name of the fiber to load.
        clad_refractive_index : float
            The refractive index of the cladding material.
        position : Tuple[float, float], optional
            The spatial position of the fiber, defaulting to (0, 0).
        remove_cladding : bool, optional
            Whether to exclude the cladding layer from the fiber configuration. Defaults to False.

        Returns
        -------
        GenericFiber
            A configured GenericFiber object with the specified properties.
        """
        if isinstance(position, Point):
            position = (position.x, position.y)

        fiber = GenericFiber(position=position)
        fiber_dict = self.load_fiber_as_dict(fiber_name=fiber_name, clad_refractive_index=clad_refractive_index)

        for structure in fiber_dict['layers'].values():
            if remove_cladding and 'cladding' in structure['name'].lower():
                continue
            fiber.create_and_add_new_structure(**structure)

        return fiber


    def make_fiber(self, structure_list: List[Dict], clad_refractive_index: float, position: Tuple[float, float] = (0, 0)) -> GenericFiber:
        """
        Construct a GenericFiber object based on a list of structural configurations.

        Parameters
        ----------
        wavelength : float
            The wavelength at which the fiber's material properties are considered.
        structure_list : List[Dict]
            A list of dictionaries, each containing the parameters for a fiber structure.
        position : Tuple[float, float], optional
            The spatial position of the fiber. Defaults to (0, 0).

        Returns
        -------
        GenericFiber
            The newly created GenericFiber object populated with specified structures.
        """
        fiber = GenericFiber(position=position)
        for structure in structure_list:
            fiber.create_and_add_new_structure(**structure)

        return fiber


    def get_fiber_file_path(self, fiber_name: str) -> Path:
        """
        Determines the file path for the given fiber name.

        Parameters
        ----------
        fiber_name : str
            The name of the fiber.

        Returns
        -------
        Path
            A Path object pointing to the fiber file.
        """
        return self.fiber_directory / f'{fiber_name}.yaml'


    def load_yaml_configuration(self, file_path: Path) -> dict:
        """
        Loads the YAML configuration from a file.

        Parameters
        ----------
        file_path : Path
            Path object pointing to the YAML file.

        Returns
        -------
        dict
            A dictionary containing the loaded YAML configuration.
        """
        with file_path.open('r') as file:
            return yaml.safe_load(file)


    def process_layers(self, layers: dict, clad_refractive_index: float = None) -> dict:
        """
        Processes the layers in the configuration, calculating indices as necessary.

        Parameters
        ----------
        layers : dict
            A dictionary of layers from the configuration.
        clad_refractive_index : float, optional
            Refractive index for material index calculation.

        Returns
        -------
        dict
            A dictionary of processed layers with calculated indices.
        """
        processed_layers = {}
        outer_layer = None
        for idx, layer in layers.items():
            layer_index = layer.get('refractive_index')
            if 'material' in layer and clad_refractive_index is not None:
                layer_index = clad_refractive_index

            elif 'NA' in layer and outer_layer:
                layer_index = np.sqrt(layer['NA']**2 + outer_layer['refractive_index']**2)

            processed_layers[idx] = {**layer, 'refractive_index': layer_index}
            outer_layer = processed_layers[idx]

        return processed_layers


    def cleanup_layers(self, layers: dict) -> dict:
        """
        Removes unnecessary keys from each layer in the dictionary.

        Parameters
        ----------
        layers : dict
            The dictionary of processed layers.

        Returns
        -------
        dict
            The cleaned-up dictionary of layers.
        """
        for layer in layers.values():
            layer.pop('NA', None)
            layer.pop('material', None)
        return layers


    def reorder_layers_if_needed(self, layers: dict, order: LayerOrder) -> dict:
        """
        Reorders the layers if required.

        Parameters
        ----------
        layers : dict
            The dictionary of layers to potentially reorder.
        order : LayerOrder
            The order to apply (LayerOrder.IN_TO_OUT or LayerOrder.OUT_TO_IN).

        Returns
        -------
        dict
            The reordered (if needed) dictionary of layers.
        """
        if order == LayerOrder.OUT_TO_IN:
            return {k: layers[k] for k in reversed(layers)}
        return layers


    def load_fiber_as_dict(self, fiber_name: str, clad_refractive_index: float = None, order: LayerOrder = LayerOrder.IN_TO_OUT) -> dict:
        """
        Main function to load and process fiber configuration.

        Parameters
        ----------
        fiber_name : str
            Name of the fiber file without extension.
        clad_refractive_index : float, optional
            Refractive index to use for material index calculation.
        order : LayerOrder, optional
            Layer order in the output dictionary; either LayerOrder.IN_TO_OUT or LayerOrder.OUT_TO_IN.

        Returns
        -------
        dict
            Dictionary containing the processed fiber configuration.
        """
        file_path = self.get_fiber_file_path(fiber_name)
        if not file_path.exists():
            available = '\n'.join(f.stem for f in file_path.parent.glob('*.yaml'))
            raise FileNotFoundError(f'Fiber file {fiber_name}.yaml not found. Available fibers: \n{available}')

        config = self.load_yaml_configuration(file_path)
        processed_layers = self.process_layers(config['layers'], clad_refractive_index)
        processed_layers = self.cleanup_layers(processed_layers)
        processed_layers = self.reorder_layers_if_needed(processed_layers, order)

        return {'layers': processed_layers}
