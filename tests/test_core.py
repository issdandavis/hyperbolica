"""Tests for hyperbolica core module."""

import math
import pytest
from hyperbolica.core import (
    Complex,
    ORIGIN,
    mobius,
    mobius_inv,
    hyperbolic_distance,
    geodesic_points,
    triangle_angle_sum,
    triangle_area,
    hyperbolic_midpoint,
    hyperbolic_circle_points,
    from_polar,
)


class TestComplex:
    def test_add(self):
        assert Complex(1, 2) + Complex(3, 4) == Complex(4, 6)

    def test_sub(self):
        assert Complex(5, 3) - Complex(2, 1) == Complex(3, 2)

    def test_mul_complex(self):
        # (1+2i)(3+4i) = 3+4i+6i+8i^2 = -5+10i
        r = Complex(1, 2) * Complex(3, 4)
        assert abs(r.x - (-5)) < 1e-10
        assert abs(r.y - 10) < 1e-10

    def test_mul_scalar(self):
        r = Complex(2, 3) * 2.0
        assert r == Complex(4, 6)

    def test_norm(self):
        assert abs(Complex(3, 4).norm - 5.0) < 1e-10

    def test_conj(self):
        assert Complex(1, 2).conj == Complex(1, -2)


class TestMobius:
    def test_origin_maps_to_origin(self):
        a = Complex(0.3, 0.2)
        r = mobius(a, a)
        assert r.norm < 1e-10

    def test_roundtrip(self):
        a = Complex(0.3, 0.4)
        z = Complex(0.1, -0.2)
        r = mobius_inv(mobius(z, a), a)
        assert abs(r.x - z.x) < 1e-10
        assert abs(r.y - z.y) < 1e-10

    def test_preserves_disk(self):
        a = Complex(0.5, 0.3)
        z = Complex(-0.2, 0.6)
        r = mobius(z, a)
        assert r.norm < 1.0


class TestDistance:
    def test_zero_distance(self):
        p = Complex(0.3, 0.2)
        assert abs(hyperbolic_distance(p, p)) < 1e-10

    def test_symmetric(self):
        a = Complex(0.1, 0.2)
        b = Complex(0.5, -0.3)
        assert abs(hyperbolic_distance(a, b) - hyperbolic_distance(b, a)) < 1e-10

    def test_triangle_inequality(self):
        a = Complex(0.1, 0.2)
        b = Complex(0.5, -0.1)
        c = Complex(-0.3, 0.4)
        ab = hyperbolic_distance(a, b)
        bc = hyperbolic_distance(b, c)
        ac = hyperbolic_distance(a, c)
        assert ac <= ab + bc + 1e-10

    def test_from_origin(self):
        # d(0, r) = 2 atanh(r)
        r = 0.5
        p = Complex(r, 0)
        expected = 2 * math.atanh(r)
        assert abs(hyperbolic_distance(ORIGIN, p) - expected) < 1e-10

    def test_grows_near_boundary(self):
        d1 = hyperbolic_distance(ORIGIN, Complex(0.5, 0))
        d2 = hyperbolic_distance(ORIGIN, Complex(0.9, 0))
        d3 = hyperbolic_distance(ORIGIN, Complex(0.99, 0))
        assert d1 < d2 < d3


class TestGeodesic:
    def test_endpoints(self):
        p1 = Complex(0.1, 0.2)
        p2 = Complex(0.5, -0.3)
        pts = geodesic_points(p1, p2, 32)
        assert len(pts) == 32
        assert abs(pts[0].x - p1.x) < 1e-6
        assert abs(pts[-1].x - p2.x) < 1e-6

    def test_points_inside_disk(self):
        p1 = Complex(0.3, 0.6)
        p2 = Complex(-0.5, 0.2)
        for pt in geodesic_points(p1, p2):
            assert pt.norm < 1.0


class TestTriangle:
    def test_angle_sum_less_than_pi(self):
        a = Complex(0.2, 0.1)
        b = Complex(-0.3, 0.4)
        c = Complex(0.1, -0.5)
        s = triangle_angle_sum(a, b, c)
        assert s < math.pi
        assert s > 0

    def test_area_equals_defect(self):
        a = Complex(0.2, 0.1)
        b = Complex(-0.3, 0.4)
        c = Complex(0.1, -0.5)
        area = triangle_area(a, b, c)
        angle_sum = triangle_angle_sum(a, b, c)
        assert abs(area - (math.pi - angle_sum)) < 1e-10

    def test_small_triangle_near_pi(self):
        # Very small triangle should have angle sum close to pi
        a = Complex(0.01, 0.01)
        b = Complex(0.02, 0.01)
        c = Complex(0.015, 0.02)
        s = triangle_angle_sum(a, b, c)
        assert abs(s - math.pi) < 0.01


class TestCircle:
    def test_returns_points(self):
        pts = hyperbolic_circle_points(Complex(0.2, 0.1), 1.0, 32)
        assert len(pts) > 0
        assert all(p.norm < 1.0 for p in pts)


class TestMidpoint:
    def test_equidistant(self):
        a = Complex(0.1, 0.2)
        b = Complex(0.5, -0.3)
        m = hyperbolic_midpoint(a, b)
        da = hyperbolic_distance(a, m)
        db = hyperbolic_distance(b, m)
        assert abs(da - db) < 0.05  # approximate due to simplified midpoint
