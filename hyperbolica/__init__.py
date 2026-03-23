"""Hyperbolica - Hyperbolic geometry toolkit for Python.

Fast Poincaré disk operations, terrain generation, and tessellations.

Free tier: core math (Möbius transforms, geodesics, distances)
Pro tier: terrain generation, tilings, batch operations, API access
"""

__version__ = "0.1.0"

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

__all__ = [
    "Complex",
    "mobius",
    "mobius_inv",
    "hyperbolic_distance",
    "geodesic_points",
    "from_polar",
    "HyperbolicTerrain",
    "HyperbolicTiling",
]
