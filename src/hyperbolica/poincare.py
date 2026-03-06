from __future__ import annotations

import math
from typing import Sequence

_EPS = 1e-12


def _norm_sq(x: Sequence[float]) -> float:
    return sum(float(v) * float(v) for v in x)


def project_to_ball(x: Sequence[float], margin: float = 1e-9) -> list[float]:
    """Project vector into the open unit ball if necessary."""
    vals = [float(v) for v in x]
    n2 = _norm_sq(vals)
    if n2 < 1.0:
        return vals
    if n2 <= 0.0:
        return vals
    scale = (1.0 - margin) / math.sqrt(n2)
    return [v * scale for v in vals]


def poincare_distance(u: Sequence[float], v: Sequence[float]) -> float:
    """Poincare-ball distance.

    d(u,v)=acosh(1 + 2||u-v||^2/((1-||u||^2)(1-||v||^2)))
    """
    if len(u) != len(v):
        raise ValueError("vectors must have same dimension")

    uu = [float(x) for x in u]
    vv = [float(x) for x in v]

    nu = _norm_sq(uu)
    nv = _norm_sq(vv)
    if nu >= 1.0 or nv >= 1.0:
        raise ValueError("points must lie strictly inside unit ball")

    diff_sq = sum((a - b) * (a - b) for a, b in zip(uu, vv))
    denom = max((1.0 - nu) * (1.0 - nv), _EPS)
    arg = 1.0 + (2.0 * diff_sq) / denom
    return math.acosh(max(arg, 1.0))


def mobius_add(u: Sequence[float], v: Sequence[float]) -> list[float]:
    """Möbius addition on the Poincare ball."""
    if len(u) != len(v):
        raise ValueError("vectors must have same dimension")

    uu = [float(x) for x in u]
    vv = [float(x) for x in v]

    nu = _norm_sq(uu)
    nv = _norm_sq(vv)
    uv = sum(a * b for a, b in zip(uu, vv))

    denom = 1.0 + 2.0 * uv + nu * nv
    if abs(denom) < _EPS:
        raise ValueError("mobius_add denominator too small")

    a = 1.0 + 2.0 * uv + nv
    b = 1.0 - nu
    out = [(a * x + b * y) / denom for x, y in zip(uu, vv)]
    return project_to_ball(out)
