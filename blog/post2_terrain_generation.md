# How to Generate Infinite Terrain Without Tiling Artifacts

*A deep dive into hyperbolic terrain generation with code*

---

Every procedural terrain generator has the same dirty secret: **it tiles**. Perlin noise repeats. Diamond-square repeats. Your players notice. Speedrunners memorize the patterns.

What if the math itself guaranteed no repetition? That's what hyperbolic terrain generation gives you.

## The Key Insight

In Euclidean space, a circle of radius r has circumference 2πr — linear growth. In hyperbolic space, a circle of radius r has circumference 2π·sinh(r) — **exponential growth**.

This means as you explore outward from any point, there's exponentially more terrain to fill. The noise function can't tile because there's too much new space.

## The Algorithm

Here's the full pipeline:

### Step 1: Poincaré Disk Coordinates

We work in the Poincaré disk — the entire infinite hyperbolic plane mapped into a unit circle. Points are complex numbers with |z| < 1.

### Step 2: Warp the Noise Coordinates

The key trick is scaling the noise input by the hyperbolic metric factor:

```python
def height_at(self, point):
    r = point.norm
    if r >= 0.999:
        return 0.0
    # This is the magic: scale factor from the Poincaré metric
    scale = 0.3 / (1 - r*r + 0.01)
    return fbm(point.x * scale + 5.3, point.y * scale + 2.7)
```

The factor `1/(1 - r²)` is the conformal factor of the Poincaré disk metric. Near the boundary (r → 1), this blows up — meaning noise coordinates spread out infinitely, so the terrain never tiles.

### Step 3: Navigate with Möbius Transforms

To "move" through the terrain, we apply a Möbius transformation. This is an isometry of hyperbolic space — it preserves all distances and angles.

```python
from hyperbolica import Complex, mobius_inv, HyperbolicTerrain

terrain = HyperbolicTerrain(seed=42)

# Look at terrain from a different viewpoint
viewpoint = Complex(0.6, 0.3)
screen_point = Complex(0.1, -0.2)

# Transform screen coords to world coords
world_point = mobius_inv(screen_point, viewpoint)
height = terrain.height_at(world_point)
```

The viewer always sits at the disk center. The world moves around them. This is computationally elegant and avoids coordinate singularities.

### Step 4: Fractal Brownian Motion

Standard fBm, nothing fancy:

```
fbm(x, y) = Σ (0.5^i) · noise(x · 2^i, y · 2^i)  for i = 0..4
```

But because the input coordinates are hyperbolically warped, the output has infinite detail near the disk boundary.

## Results

With the `hyperbolica` package:

```python
terrain = HyperbolicTerrain(seed=42, palette="arctic")
grid = terrain.height_map(resolution=256)

# Each pixel's height is deterministic, seed-dependent, and never repeats
# Perfect for game worlds, art, or data visualization
```

Available palettes: `ocean`, `volcanic`, `arctic`, `alien`.

## Why This Matters for Games

1. **No tiling** — Mathematically impossible to repeat
2. **Infinite LOD** — Detail increases exponentially toward the boundary
3. **Cheap navigation** — Möbius transforms are just complex arithmetic (4 multiplies, 2 adds)
4. **Deterministic** — Same seed = same world, always
5. **Natural hierarchy** — Rivers, mountains, valleys branch naturally in hyperbolic space

## Get Started

```bash
pip install hyperbolica
```

API access for real-time terrain generation: `api.hyperbolica.dev` (Pro tier, $29/mo).

---

*Next post: Hyperbolic tilings and why Escher was doing computational geometry in 1958.*
