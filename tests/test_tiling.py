"""Tests for hyperbolic tiling module."""

import pytest
from hyperbolica.tiling import HyperbolicTiling


class TestTiling:
    def test_invalid_tiling_raises(self):
        with pytest.raises(ValueError, match="not hyperbolic"):
            HyperbolicTiling(p=4, q=4)  # Euclidean

    def test_valid_tiling_generates(self):
        t = HyperbolicTiling(p=5, q=4, max_tiles=50)
        assert t.num_tiles > 0

    def test_vertices_inside_disk(self):
        t = HyperbolicTiling(p=5, q=4, max_tiles=100)
        for tile in t.tiles:
            for v in tile:
                assert v.norm < 1.01  # small tolerance

    def test_correct_vertex_count(self):
        t = HyperbolicTiling(p=7, q=3, max_tiles=50)
        for tile in t.tiles:
            assert len(tile) == 7

    def test_svg_output(self):
        t = HyperbolicTiling(p=5, q=4, max_tiles=20)
        svg = t.to_svg(400)
        assert svg.startswith("<svg")
        assert "polygon" in svg

    def test_dict_output(self):
        t = HyperbolicTiling(p=5, q=4, max_tiles=20)
        d = t.to_dict()
        assert d["p"] == 5
        assert d["q"] == 4
        assert len(d["tiles"]) == d["num_tiles"]

    def test_various_tilings(self):
        valid = [(5, 4), (7, 3), (3, 7), (4, 5), (6, 4), (8, 3)]
        for p, q in valid:
            t = HyperbolicTiling(p=p, q=q, max_tiles=30)
            assert t.num_tiles > 0
