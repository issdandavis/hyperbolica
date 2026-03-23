"""Tests for terrain generation."""

from hyperbolica.core import Complex, ORIGIN
from hyperbolica.terrain import HyperbolicTerrain


class TestTerrain:
    def test_deterministic_with_seed(self):
        t1 = HyperbolicTerrain(seed=42)
        t2 = HyperbolicTerrain(seed=42)
        assert t1.height_at(Complex(0.3, 0.2)) == t2.height_at(Complex(0.3, 0.2))

    def test_different_seeds_differ(self):
        t1 = HyperbolicTerrain(seed=42)
        t2 = HyperbolicTerrain(seed=99)
        assert t1.height_at(Complex(0.3, 0.2)) != t2.height_at(Complex(0.3, 0.2))

    def test_height_range(self):
        t = HyperbolicTerrain(seed=42)
        for x in range(-8, 9, 2):
            for y in range(-8, 9, 2):
                pt = Complex(x * 0.1, y * 0.1)
                if pt.norm < 0.95:
                    h = t.height_at(pt)
                    assert 0 <= h <= 1.0

    def test_boundary_returns_zero(self):
        t = HyperbolicTerrain(seed=42)
        assert t.height_at(Complex(0.9999, 0.0)) == 0.0

    def test_color_at(self):
        t = HyperbolicTerrain(seed=42, palette="volcanic")
        c = t.color_at(Complex(0.3, 0.2))
        assert len(c) == 3
        assert all(0 <= v <= 255 for v in c)

    def test_sample_grid(self):
        t = HyperbolicTerrain(seed=42)
        samples = t.sample_grid(resolution=16)
        assert len(samples) > 0
        assert "height" in samples[0]
        assert "color" in samples[0]

    def test_height_map(self):
        t = HyperbolicTerrain(seed=42)
        grid = t.height_map(resolution=16)
        assert len(grid) == 16
        assert len(grid[0]) == 16

    def test_palettes(self):
        for name in HyperbolicTerrain.PALETTES:
            t = HyperbolicTerrain(seed=1, palette=name)
            c = t.color_at(Complex(0.2, 0.1))
            assert len(c) == 3
