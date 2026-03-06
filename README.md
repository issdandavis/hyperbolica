# Hyperbolica

`hyperbolica` is a focused geometry package for hyperbolic (Poincare-ball) operations that can be reused across AI routing, semantic indexing, and spatial simulation workflows.

## Install

```bash
pip install hyperbolica
```

## Included in v0.1
- Poincare-ball distance
- Mobius addition
- Safe projection into the open unit ball
- Tiny CLI for quick checks

## Quick usage

```python
from hyperbolica import poincare_distance

u = [0.1, 0.2]
v = [0.3, 0.1]
print(poincare_distance(u, v))
```

## Monetization path
- Open core on PyPI
- Pro add-on package (`hyperbolica-pro`) for advanced indexing + hosted API
- Enterprise support for integration and performance tuning

## Pricing (initial)
- Open Core: `$0`
- Pro Pack: `$79` one-time
- Hosted API: `$29/mo`

## Landing page
- GitHub Pages source: `docs/index.html`
- URL after Pages is enabled in repo settings: `https://issdandavis.github.io/hyperbolica/`
