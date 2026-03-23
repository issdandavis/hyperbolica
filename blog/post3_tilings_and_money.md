# The Math Behind HyperRogue: Hyperbolic Tilings Explained (With Code)

*And why this niche math library is a real business*

---

In 2011, a Polish mathematician named Zeno Rogue released HyperRogue — a roguelike game set entirely in hyperbolic space. It used {7,3} tilings (heptagons, 3 at each vertex). The game has sold over 100,000 copies on Steam.

That's the market signal: people will pay for hyperbolic geometry.

## What Makes Hyperbolic Tilings Special

In Euclidean space, exactly 3 regular tilings exist: triangles {3,6}, squares {4,4}, hexagons {6,3}.

In hyperbolic space, **infinitely many** regular tilings exist. Any {p,q} where (p-2)(q-2) > 4 works.

```python
from hyperbolica import HyperbolicTiling

# The classic HyperRogue tiling
tiling = HyperbolicTiling(p=7, q=3)
print(f"Tiles: {tiling.num_tiles}")

# Escher's Circle Limit III used {8,3}
escher = HyperbolicTiling(p=8, q=3)
svg = escher.to_svg(800)  # Publication-quality SVG

# Try exotic ones
exotic = HyperbolicTiling(p=5, q=5, max_tiles=400)
```

## The Algorithm

### 1. Compute Fundamental Polygon Size

For a {p,q} tiling, the vertex radius in the Poincaré disk is:

```
edge_r = sqrt((cos²(π/p) - sin²(π/q)) / (1 - sin²(π/q)))
```

This formula comes from the hyperbolic law of cosines applied to the Schwarz triangle.

### 2. Generate by Reflection

Start with one polygon at the origin. For each edge, reflect across it using Möbius transformations to find the neighbor. Repeat recursively.

The reflection across a geodesic through midpoint `m`:
1. Translate `m` to origin (Möbius transform)
2. Negate (reflect through origin)
3. Translate back

### 3. Deduplicate

Hash tile centers at integer precision to avoid duplicates. Tiles near the boundary get exponentially small in Euclidean terms, so we cap at a configurable `max_tiles`.

## Output Formats

```python
# JSON for game engines
data = tiling.to_dict()
# Returns: {"p": 7, "q": 3, "num_tiles": 342, "tiles": [[{x, y}, ...], ...]}

# SVG for web/print
svg = tiling.to_svg(600)

# Or use the API
# POST api.hyperbolica.dev/v1/tiling {"p": 7, "q": 3, "format": "svg"}
```

## Who Pays for This

1. **Game developers** building non-Euclidean worlds (Unity, Godot, custom engines)
2. **Artists and designers** generating Escher-style patterns
3. **Mathematicians and educators** creating interactive demonstrations
4. **ML researchers** working with Poincaré embeddings and hyperbolic neural networks

The `hyperbolica` Python package handles the core math. The API handles real-time generation for web apps and games that can't ship a Python dependency.

## Pricing

- **PyPI package**: Free (core math). Pro features (terrain + tilings) coming as `hyperbolica[pro]`.
- **API**: Free tier (100 req/day), Pro ($29/mo), Enterprise ($199/mo)

---

*Try it: `pip install hyperbolica` or hit `api.hyperbolica.dev/docs`*
