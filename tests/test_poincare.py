from __future__ import annotations

import math

import pytest

from hyperbolica import mobius_add, poincare_distance, project_to_ball


def test_poincare_distance_zero() -> None:
    u = [0.1, 0.2, 0.05]
    assert poincare_distance(u, u) == pytest.approx(0.0, abs=1e-12)


def test_poincare_distance_symmetric() -> None:
    u = [0.1, 0.2]
    v = [0.2, 0.1]
    assert poincare_distance(u, v) == pytest.approx(poincare_distance(v, u), rel=1e-12)


def test_poincare_distance_rejects_outside_ball() -> None:
    with pytest.raises(ValueError):
        poincare_distance([1.0, 0.0], [0.0, 0.0])


def test_project_to_ball_clamps_norm() -> None:
    out = project_to_ball([3.0, 4.0])
    norm = math.sqrt(sum(x * x for x in out))
    assert norm < 1.0


def test_mobius_add_dimension_mismatch() -> None:
    with pytest.raises(ValueError):
        mobius_add([0.1], [0.2, 0.3])


def test_mobius_add_stays_in_ball() -> None:
    out = mobius_add([0.1, 0.2], [0.2, 0.1])
    norm_sq = sum(x * x for x in out)
    assert norm_sq < 1.0
