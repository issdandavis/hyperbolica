"""Hyperbolic terrain generation using fractal Brownian motion in the Poincaré disk.

PRO FEATURE - included in hyperbolica[pro] and API access.
"""

from __future__ import annotations

import math
import random
from typing import Optional

from hyperbolica.core import Complex, mobius, mobius_inv, hyperbolic_distance, ORIGIN


class HyperbolicTerrain:
    """Generate procedural terrain in hyperbolic space.

    The terrain uses fractal Brownian motion (fBm) with coordinates warped
    by the hyperbolic metric, producing infinite non-repeating landscapes
    with natural hierarchical branching.
    """

    PALETTES = {
        "ocean": [
            (10, 30, 60), (20, 80, 120), (40, 160, 140),
            (120, 200, 120), (200, 220, 160), (240, 240, 200),
        ],
        "volcanic": [
            (20, 5, 10), (80, 15, 10), (160, 40, 10),
            (220, 100, 20), (240, 180, 60), (255, 240, 200),
        ],
        "arctic": [
            (15, 20, 40), (30, 50, 90), (60, 100, 150),
            (140, 180, 210), (200, 220, 240), (240, 248, 255),
        ],
        "alien": [
            (10, 5, 30), (40, 10, 80), (100, 20, 140),
            (60, 150, 100), (120, 220, 80), (200, 255, 160),
        ],
    }

    def __init__(self, seed: Optional[int] = None, palette: str = "ocean"):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.palette_name = palette
        self.palette = self.PALETTES.get(palette, self.PALETTES["ocean"])
        self.view_center = Complex(0.0, 0.0)

    def _hash(self, x: int, y: int) -> float:
        h = self.seed + x * 374761393 + y * 668265263
        h = math.sin(h) * 43758.5453
        return h - math.floor(h)

    def _smooth_noise(self, x: float, y: float) -> float:
        ix, iy = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - ix, y - iy
        sx = fx * fx * (3 - 2 * fx)
        sy = fy * fy * (3 - 2 * fy)
        return (
            self._hash(ix, iy) * (1 - sx) * (1 - sy)
            + self._hash(ix + 1, iy) * sx * (1 - sy)
            + self._hash(ix, iy + 1) * (1 - sx) * sy
            + self._hash(ix + 1, iy + 1) * sx * sy
        )

    def _fbm(self, x: float, y: float, octaves: int = 5) -> float:
        value, amplitude, frequency = 0.0, 0.5, 1.0
        for _ in range(octaves):
            value += amplitude * self._smooth_noise(x * frequency, y * frequency)
            amplitude *= 0.5
            frequency *= 2.0
        return value

    def height_at(self, point: Complex) -> float:
        """Get terrain height at a point in the Poincaré disk.

        Args:
            point: A Complex point inside the unit disk.

        Returns:
            Height value between 0 and 1.
        """
        r = point.norm
        if r >= 0.999:
            return 0.0
        scale = 0.3 / (1 - r * r + 0.01)
        return self._fbm(point.x * scale + 5.3, point.y * scale + 2.7)

    def color_at(self, point: Complex) -> tuple[int, int, int]:
        """Get terrain color (RGB) at a point."""
        h = self.height_at(point)
        return self._interpolate_color(h)

    def _interpolate_color(self, h: float) -> tuple[int, int, int]:
        pal = self.palette
        t = max(0.0, min(1.0, h)) * (len(pal) - 1)
        i = int(math.floor(t))
        f = t - i
        if i >= len(pal) - 1:
            return pal[-1]
        return tuple(int(pal[i][j] + (pal[i + 1][j] - pal[i][j]) * f) for j in range(3))

    def navigate_to(self, target: Complex) -> None:
        """Move the view center to a new point."""
        if target.norm < 0.999:
            self.view_center = target

    def sample_grid(
        self,
        resolution: int = 128,
        radius: float = 0.98,
    ) -> list[dict]:
        """Sample terrain on a grid, returning height and color data.

        Args:
            resolution: Grid size (resolution x resolution).
            radius: Maximum disk radius to sample.

        Returns:
            List of dicts with keys: x, y, height, color, hyp_dist
        """
        samples = []
        for py in range(resolution):
            for px in range(resolution):
                dx = (2.0 * px / (resolution - 1) - 1.0) * radius
                dy = (2.0 * py / (resolution - 1) - 1.0) * radius
                disk_pt = Complex(dx, dy)
                if disk_pt.norm >= radius:
                    continue
                world_pt = mobius_inv(disk_pt, self.view_center)
                if world_pt.norm >= 0.999:
                    continue
                h = self.height_at(world_pt)
                color = self._interpolate_color(h)
                samples.append({
                    "x": dx,
                    "y": dy,
                    "height": round(h, 4),
                    "color": color,
                    "hyp_dist": round(hyperbolic_distance(ORIGIN, world_pt), 4),
                })
        return samples

    def height_map(self, resolution: int = 128) -> list[list[float]]:
        """Generate a 2D height map as a nested list.

        Useful for feeding into visualization or game engines.
        """
        grid = []
        for py in range(resolution):
            row = []
            for px in range(resolution):
                dx = 2.0 * px / (resolution - 1) - 1.0
                dy = 2.0 * py / (resolution - 1) - 1.0
                pt = Complex(dx * 0.95, dy * 0.95)
                if pt.norm >= 0.98:
                    row.append(0.0)
                else:
                    world = mobius_inv(pt, self.view_center)
                    row.append(round(self.height_at(world), 4))
            grid.append(row)
        return grid
