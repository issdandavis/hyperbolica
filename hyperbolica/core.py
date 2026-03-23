"""Core hyperbolic geometry operations on the Poincaré disk model.

All points are represented as complex numbers (x + yi) inside the unit disk.
"""

from __future__ import annotations

import math
from typing import NamedTuple


class Complex(NamedTuple):
    """A point in the Poincaré disk (or a complex number)."""
    x: float
    y: float

    def __add__(self, other: Complex) -> Complex:
        return Complex(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Complex) -> Complex:
        return Complex(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Complex(self.x * other, self.y * other)
        return Complex(
            self.x * other.x - self.y * other.y,
            self.x * other.y + self.y * other.x,
        )

    def __neg__(self) -> Complex:
        return Complex(-self.x, -self.y)

    @property
    def conj(self) -> Complex:
        return Complex(self.x, -self.y)

    @property
    def norm(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def norm_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Complex:
        n = self.norm
        if n < 1e-15:
            return Complex(0.0, 0.0)
        return Complex(self.x / n, self.y / n)


ORIGIN = Complex(0.0, 0.0)
ONE = Complex(1.0, 0.0)


def cdiv(a: Complex, b: Complex) -> Complex:
    """Complex division a / b."""
    d = b.norm_sq
    if d < 1e-15:
        return ORIGIN
    return Complex(
        (a.x * b.x + a.y * b.y) / d,
        (a.y * b.x - a.x * b.y) / d,
    )


def from_polar(r: float, theta: float) -> Complex:
    """Create a point from polar coordinates."""
    return Complex(r * math.cos(theta), r * math.sin(theta))


def mobius(z: Complex, a: Complex) -> Complex:
    """Möbius transformation: translate point `a` to origin.

    Maps the Poincaré disk to itself, sending `a` to 0.
    Formula: (z - a) / (1 - conj(a) * z)
    """
    return cdiv(z - a, ONE - a.conj * z)


def mobius_inv(z: Complex, a: Complex) -> Complex:
    """Inverse Möbius transformation: translate origin to point `a`.

    Formula: (z + a) / (1 + conj(a) * z)
    """
    return cdiv(z + a, ONE + a.conj * z)


def hyperbolic_distance(a: Complex, b: Complex) -> float:
    """Compute the hyperbolic distance between two points in the Poincaré disk.

    Returns infinity if either point is on the boundary.
    """
    r = mobius(b, a).norm
    if r >= 1.0:
        return float("inf")
    return 2.0 * math.atanh(r)


def geodesic_points(
    p1: Complex, p2: Complex, num_points: int = 64
) -> list[Complex]:
    """Compute points along the geodesic (shortest path) between p1 and p2.

    In the Poincaré disk, geodesics are circular arcs orthogonal to the
    boundary circle, or diameters through the center.

    Returns a list of Complex points tracing the geodesic.
    """
    # Translate p1 to origin; the geodesic becomes a diameter
    p2_translated = mobius(p2, p1)
    direction = p2_translated.normalized()
    dist = p2_translated.norm

    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        r = dist * t
        local = Complex(direction.x * r, direction.y * r)
        world = mobius_inv(local, p1)
        points.append(world)
    return points


def hyperbolic_midpoint(a: Complex, b: Complex) -> Complex:
    """Find the hyperbolic midpoint between two points."""
    b_translated = mobius(b, a)
    # The hyperbolic midpoint in disk coords: tanh(d/4) in the direction of b
    full_r = b_translated.norm
    if full_r < 1e-15:
        return a
    half_hyp = math.atanh(full_r)  # half the hyperbolic distance
    mid_r = math.tanh(half_hyp / 2.0)
    direction = b_translated.normalized()
    mid_local = Complex(direction.x * mid_r, direction.y * mid_r)
    return mobius_inv(mid_local, a)


def hyperbolic_circle_points(
    center: Complex, hyp_radius: float, num_points: int = 64
) -> list[Complex]:
    """Generate points on a hyperbolic circle.

    A hyperbolic circle in the Poincaré disk is also a Euclidean circle
    (but with a different center and radius).
    """
    disk_radius = math.tanh(hyp_radius / 2.0)
    points = []
    for i in range(num_points):
        angle = (i / num_points) * 2.0 * math.pi
        local = from_polar(disk_radius, angle)
        world = mobius_inv(local, center)
        if world.norm < 1.0:
            points.append(world)
    return points


def triangle_angle_sum(a: Complex, b: Complex, c: Complex) -> float:
    """Compute the angle sum of a hyperbolic triangle.

    In hyperbolic geometry, this is always less than pi.
    The defect (pi - angle_sum) equals the area.
    """
    def angle_at(vertex, p1, p2):
        t1 = mobius(p1, vertex)
        t2 = mobius(p2, vertex)
        a1 = math.atan2(t1.y, t1.x)
        a2 = math.atan2(t2.y, t2.x)
        diff = abs(a1 - a2)
        if diff > math.pi:
            diff = 2 * math.pi - diff
        return diff

    return angle_at(a, b, c) + angle_at(b, a, c) + angle_at(c, a, b)


def triangle_area(a: Complex, b: Complex, c: Complex) -> float:
    """Compute the area of a hyperbolic triangle (equals pi - angle_sum)."""
    return math.pi - triangle_angle_sum(a, b, c)
