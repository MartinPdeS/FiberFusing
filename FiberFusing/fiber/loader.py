#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import numpy as np
from pathlib import Path
from MPSTools.material_catalogue.loader import get_material_index


def get_fiber_file_path(fiber_name: str) -> Path:
    """
    Determines the file path for the given fiber name.

    Parameters:
    - fiber_name: The name of the fiber.

    Returns:
    - A Path object pointing to the fiber file.
    """
    return Path(__file__).parent / 'fiber_files' / f'{fiber_name}.yaml'


def load_yaml_configuration(file_path: Path) -> dict:
    """
    Loads the YAML configuration from a file.

    Parameters:
    - file_path: Path object pointing to the YAML file.

    Returns:
    - A dictionary containing the loaded YAML configuration.
    """
    with file_path.open('r') as file:
        return yaml.safe_load(file)


def process_layers(layers: dict, wavelength: float = None) -> dict:
    """
    Processes the layers in the configuration, calculating indices as necessary.

    Parameters:
    - layers: A dictionary of layers from the configuration.
    - wavelength: Optional; wavelength for material index calculation.

    Returns:
    - A dictionary of processed layers with calculated indices.
    """
    processed_layers = {}
    outer_layer = None
    for idx, layer in layers.items():
        layer_index = layer.get('index')
        if 'material' in layer and wavelength:
            layer_index = get_material_index(layer['material'], wavelength)
        elif 'NA' in layer and outer_layer:
            layer_index = np.sqrt(layer['NA']**2 + outer_layer['index']**2)

        processed_layers[idx] = {**layer, 'index': layer_index}
        outer_layer = processed_layers[idx]

    return processed_layers


def cleanup_layers(layers: dict) -> dict:
    """
    Removes unnecessary keys from each layer in the dictionary.

    Parameters:
    - layers: The dictionary of processed layers.

    Returns:
    - The cleaned-up dictionary of layers.
    """
    for layer in layers.values():
        layer.pop('NA', None)
        layer.pop('material', None)
    return layers


def reorder_layers_if_needed(layers: dict, order: str) -> dict:
    """
    Reorders the layers if required.

    Parameters:
    - layers: The dictionary of layers to potentially reorder.
    - order: The order to apply ('in-to-out' or 'out-to-in').

    Returns:
    - The reordered (if needed) dictionary of layers.
    """
    if order == 'out-to-in':
        return {k: layers[k] for k in reversed(layers)}
    return layers


def load_fiber_as_dict(fiber_name: str, wavelength: float = None, order: str = 'in-to-out') -> dict:
    """
    Main function to load and process fiber configuration.

    Parameters:
    - fiber_name: Name of the fiber file without extension.
    - wavelength: Optional; wavelength to use for material index calculation.
    - order: Layer order in the output dictionary; either 'in-to-out' or 'out-to-in'.

    Returns:
    - Dictionary containing the processed fiber configuration.
    """
    file_path = get_fiber_file_path(fiber_name)
    if not file_path.exists():
        available = '\n'.join(f.stem for f in file_path.parent.glob('*.yaml'))
        raise FileNotFoundError(f'Fiber file {fiber_name}.yaml not found. Available fibers: \n{available}')

    config = load_yaml_configuration(file_path)
    processed_layers = process_layers(config['layers'], wavelength)
    processed_layers = cleanup_layers(processed_layers)
    processed_layers = reorder_layers_if_needed(processed_layers, order)

    return {'layers': processed_layers}

# -
