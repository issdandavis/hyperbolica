# Hyperbolica

Hyperbolic geometry toolkit for Python. Poincaré disk operations, procedural terrain generation, and tessellations.

## Install

```bash
pip install hyperbolica
```

## Quick Start

```python
from hyperbolica import Complex, hyperbolic_distance, HyperbolicTerrain, HyperbolicTiling

# Compute hyperbolic distance
a = Complex(0.3, 0.2)
b = Complex(-0.5, 0.1)
print(hyperbolic_distance(a, b))  # 1.832...

# Generate terrain
terrain = HyperbolicTerrain(seed=42, palette="volcanic")
height = terrain.height_at(Complex(0.3, 0.2))

# Create a {5,4} tiling
tiling = HyperbolicTiling(p=5, q=4)
svg = tiling.to_svg()
```

## API

Full API docs at https://hyperbolica.dev/docs
