"""Hyperbolica - Hyperbolic geometry toolkit for Python.

Fast Poincaré disk operations, terrain generation, and tessellations.

Free tier: core math (Möbius transforms, geodesics, distances)
Pro tier: terrain generation, tilings, batch operations, API access
"""

__version__ = "0.1.0"

import importlib.util
import os as _os

from hyperbolica.core import (
    Complex,
    mobius,
    mobius_inv,
    hyperbolic_distance,
    geodesic_points,
    from_polar,
)
from hyperbolica.terrain import HyperbolicTerrain
from hyperbolica.tiling import HyperbolicTiling

# Load n-dimensional Poincaré ball operations from src/hyperbolica/poincare.py
_poincare_path = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
    "src", "hyperbolica", "poincare.py",
)
_spec = importlib.util.spec_from_file_location("hyperbolica._poincare", _poincare_path)
_poincare_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_poincare_mod)

poincare_distance = _poincare_mod.poincare_distance
mobius_add = _poincare_mod.mobius_add
project_to_ball = _poincare_mod.project_to_ball

__all__ = [
    "Complex",
    "mobius",
    "mobius_inv",
    "hyperbolic_distance",
    "geodesic_points",
    "from_polar",
    "HyperbolicTerrain",
    "HyperbolicTiling",
    "poincare_distance",
    "mobius_add",
    "project_to_ball",
]
