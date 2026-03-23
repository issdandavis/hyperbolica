"""Hyperbolic tessellations ({p,q} tilings) in the Poincaré disk.

PRO FEATURE - included in hyperbolica[pro] and API access.
"""

from __future__ import annotations

import math
from hyperbolica.core import Complex, from_polar, mobius, mobius_inv, ORIGIN


class HyperbolicTiling:
    """Generate regular {p,q} tessellations of the hyperbolic plane.

    A {p,q} tiling uses regular p-gons with q meeting at each vertex.
    Valid hyperbolic tilings require (p-2)(q-2) > 4.
    """

    def __init__(self, p: int = 5, q: int = 4, max_tiles: int = 600):
        if (p - 2) * (q - 2) <= 4:
            raise ValueError(
                f"{{{p},{q}}} is not hyperbolic. Need (p-2)(q-2) > 4. "
                f"Got {(p-2)*(q-2)}."
            )
        self.p = p
        self.q = q
        self.max_tiles = max_tiles
        self._tiles: list[list[Complex]] | None = None

    @property
    def tiles(self) -> list[list[Complex]]:
        """List of tiles, each a list of vertex Complex points."""
        if self._tiles is None:
            self._tiles = self._generate()
        return self._tiles

    @property
    def edge_radius(self) -> float:
        """Disk radius of polygon vertices."""
        cos_p = math.cos(math.pi / self.p)
        sin_q = math.sin(math.pi / self.q)
        val = (cos_p ** 2 - sin_q ** 2) / (1 - sin_q ** 2)
        return math.sqrt(max(0, val))

    @property
    def num_tiles(self) -> int:
        return len(self.tiles)

    def _make_polygon(self, center: Complex, angle: float) -> list[Complex]:
        """Create a regular p-gon centered at `center`."""
        edge_r = self.edge_radius
        verts = []
        for i in range(self.p):
            a = angle + 2 * math.pi * i / self.p
            vert = from_polar(edge_r, a)
            # Translate from origin to center
            verts.append(mobius_inv(vert, center))
        return verts

    def _poly_key(self, verts: list[Complex]) -> str:
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        return f"{int(cx * 200)},{int(cy * 200)}"

    def _generate(self) -> list[list[Complex]]:
        result = []
        visited: set[str] = set()
        queue: list[tuple[Complex, float, int]] = []

        def add_tile(center: Complex, angle: float, depth: int):
            verts = self._make_polygon(center, angle)
            if center.norm > 0.97:
                if any(v.norm > 0.98 for v in verts):
                    return
            key = self._poly_key(verts)
            if key in visited:
                return
            visited.add(key)
            result.append(verts)
            if depth <= 0 or len(result) >= self.max_tiles:
                return

            for i in range(self.p):
                v1, v2 = verts[i], verts[(i + 1) % self.p]
                mid = Complex((v1.x + v2.x) / 2, (v1.y + v2.y) / 2)
                tc = mobius(center, mid)
                reflected = mobius_inv(Complex(-tc.x, -tc.y), mid)
                if reflected.norm < 0.97:
                    queue.append((reflected, angle + math.pi / self.p, depth - 1))

        add_tile(ORIGIN, math.pi / self.p, 5)
        safety = 0
        while queue and len(result) < self.max_tiles and safety < 5000:
            safety += 1
            c, a, d = queue.pop(0)
            add_tile(c, a, d)

        return result

    def to_svg(self, size: int = 500) -> str:
        """Export the tiling as an SVG string."""
        r = size / 2 - 5
        cx, cy = size / 2, size / 2
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0d1520" stroke="#2a4a6a" stroke-width="2"/>',
        ]
        for ti, verts in enumerate(self.tiles):
            hue = (ti * 37) % 360
            pts = " ".join(f"{cx + v.x * r:.1f},{cy + v.y * r:.1f}" for v in verts)
            lines.append(
                f'<polygon points="{pts}" fill="hsla({hue},50%,25%,0.6)" '
                f'stroke="rgba(100,180,240,0.5)" stroke-width="1"/>'
            )
        lines.append("</svg>")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Export tiling data as a JSON-serializable dict."""
        return {
            "p": self.p,
            "q": self.q,
            "num_tiles": len(self.tiles),
            "tiles": [
                [{"x": round(v.x, 6), "y": round(v.y, 6)} for v in tile]
                for tile in self.tiles
            ],
        }
