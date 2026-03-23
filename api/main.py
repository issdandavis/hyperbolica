"""Hyperbolica SaaS API - Hyperbolic geometry as a service.

Free tier: 100 requests/day (core math only)
Pro tier: $29/mo - unlimited requests, terrain, tilings, batch ops
Enterprise: $199/mo - dedicated instance, priority support, SLA
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import defaultdict
from functools import wraps

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from hyperbolica.core import (
    Complex,
    hyperbolic_distance,
    geodesic_points,
    triangle_angle_sum,
    triangle_area,
    hyperbolic_circle_points,
    hyperbolic_midpoint,
    from_polar,
)
from hyperbolica.terrain import HyperbolicTerrain
from hyperbolica.tiling import HyperbolicTiling

app = FastAPI(
    title="Hyperbolica API",
    description="Hyperbolic geometry computations as a service. "
    "Poincaré disk operations, terrain generation, and tessellations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rate limiting (in-memory for demo; use Redis in production)
# ---------------------------------------------------------------------------
RATE_LIMITS = {"free": 100, "pro": 10000, "enterprise": 100000}
_request_counts: dict[str, list[float]] = defaultdict(list)

# Demo API keys (in production, use a database)
API_KEYS = {
    "demo-free-key": "free",
    "demo-pro-key": "pro",
}


def get_tier(api_key: str | None) -> str:
    if not api_key:
        return "free"
    return API_KEYS.get(api_key, "free")


def check_rate_limit(api_key: str | None):
    tier = get_tier(api_key)
    limit = RATE_LIMITS[tier]
    key = api_key or "anonymous"
    now = time.time()
    day_ago = now - 86400
    _request_counts[key] = [t for t in _request_counts[key] if t > day_ago]
    if len(_request_counts[key]) >= limit:
        raise HTTPException(
            429,
            detail=f"Rate limit exceeded ({limit}/day for {tier} tier). "
            "Upgrade at https://hyperbolica.dev/pricing",
        )
    _request_counts[key].append(now)


def require_pro(api_key: str | None):
    tier = get_tier(api_key)
    if tier == "free":
        raise HTTPException(
            403,
            detail="This endpoint requires a Pro or Enterprise subscription. "
            "Get your API key at https://hyperbolica.dev/pricing",
        )


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------
class Point(BaseModel):
    x: float = Field(..., ge=-1, le=1)
    y: float = Field(..., ge=-1, le=1)


class DistanceRequest(BaseModel):
    a: Point
    b: Point


class GeodesicRequest(BaseModel):
    p1: Point
    p2: Point
    num_points: int = Field(64, ge=2, le=512)


class TriangleRequest(BaseModel):
    a: Point
    b: Point
    c: Point


class CircleRequest(BaseModel):
    center: Point
    hyp_radius: float = Field(..., gt=0, le=20)
    num_points: int = Field(64, ge=8, le=512)


class TerrainRequest(BaseModel):
    seed: int | None = None
    palette: str = "ocean"
    resolution: int = Field(64, ge=16, le=256)
    center_x: float = Field(0.0, ge=-0.99, le=0.99)
    center_y: float = Field(0.0, ge=-0.99, le=0.99)


class TilingRequest(BaseModel):
    p: int = Field(5, ge=3, le=12)
    q: int = Field(4, ge=3, le=12)
    max_tiles: int = Field(200, ge=1, le=1000)
    format: str = Field("json", pattern="^(json|svg)$")


class BatchDistanceRequest(BaseModel):
    pairs: list[DistanceRequest] = Field(..., max_length=1000)


# ---------------------------------------------------------------------------
# FREE TIER ENDPOINTS
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "name": "Hyperbolica API",
        "version": "0.1.0",
        "docs": "/docs",
        "pricing": "https://hyperbolica.dev/pricing",
        "tiers": {
            "free": "100 req/day - core math",
            "pro": "$29/mo - terrain, tilings, batch ops",
            "enterprise": "$199/mo - dedicated, SLA",
        },
    }


@app.post("/v1/distance")
def compute_distance(
    req: DistanceRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    a = Complex(req.a.x, req.a.y)
    b = Complex(req.b.x, req.b.y)
    d = hyperbolic_distance(a, b)
    return {"distance": round(d, 10), "unit": "hyperbolic"}


@app.post("/v1/geodesic")
def compute_geodesic(
    req: GeodesicRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    p1 = Complex(req.p1.x, req.p1.y)
    p2 = Complex(req.p2.x, req.p2.y)
    pts = geodesic_points(p1, p2, req.num_points)
    return {
        "points": [{"x": round(p.x, 8), "y": round(p.y, 8)} for p in pts],
        "length": round(hyperbolic_distance(p1, p2), 10),
    }


@app.post("/v1/triangle")
def compute_triangle(
    req: TriangleRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    a = Complex(req.a.x, req.a.y)
    b = Complex(req.b.x, req.b.y)
    c = Complex(req.c.x, req.c.y)
    angle_sum = triangle_angle_sum(a, b, c)
    area = triangle_area(a, b, c)
    return {
        "angle_sum_radians": round(angle_sum, 10),
        "angle_sum_degrees": round(angle_sum * 180 / 3.141592653589793, 6),
        "area": round(area, 10),
        "defect_degrees": round((3.141592653589793 - angle_sum) * 180 / 3.141592653589793, 6),
        "side_lengths": {
            "ab": round(hyperbolic_distance(a, b), 8),
            "bc": round(hyperbolic_distance(b, c), 8),
            "ca": round(hyperbolic_distance(c, a), 8),
        },
    }


@app.post("/v1/circle")
def compute_circle(
    req: CircleRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    center = Complex(req.center.x, req.center.y)
    pts = hyperbolic_circle_points(center, req.hyp_radius, req.num_points)
    return {
        "points": [{"x": round(p.x, 8), "y": round(p.y, 8)} for p in pts],
        "hyp_radius": req.hyp_radius,
        "hyp_circumference": round(2 * 3.141592653589793 * (2.718281828 ** req.hyp_radius - 2.718281828 ** (-req.hyp_radius)) / 2, 6),
    }


# ---------------------------------------------------------------------------
# PRO TIER ENDPOINTS
# ---------------------------------------------------------------------------
@app.post("/v1/terrain")
def generate_terrain(
    req: TerrainRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    require_pro(x_api_key)
    terrain = HyperbolicTerrain(seed=req.seed, palette=req.palette)
    terrain.navigate_to(Complex(req.center_x, req.center_y))
    samples = terrain.sample_grid(resolution=req.resolution)
    return {
        "seed": terrain.seed,
        "palette": req.palette,
        "resolution": req.resolution,
        "num_samples": len(samples),
        "samples": samples,
    }


@app.post("/v1/terrain/heightmap")
def generate_heightmap(
    req: TerrainRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    require_pro(x_api_key)
    terrain = HyperbolicTerrain(seed=req.seed, palette=req.palette)
    terrain.navigate_to(Complex(req.center_x, req.center_y))
    grid = terrain.height_map(resolution=req.resolution)
    return {
        "seed": terrain.seed,
        "resolution": req.resolution,
        "heightmap": grid,
    }


@app.post("/v1/tiling")
def generate_tiling(
    req: TilingRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    require_pro(x_api_key)
    tiling = HyperbolicTiling(p=req.p, q=req.q, max_tiles=req.max_tiles)
    if req.format == "svg":
        return Response(content=tiling.to_svg(), media_type="image/svg+xml")
    return tiling.to_dict()


@app.post("/v1/batch/distances")
def batch_distances(
    req: BatchDistanceRequest,
    x_api_key: str | None = Header(None),
):
    check_rate_limit(x_api_key)
    require_pro(x_api_key)
    results = []
    for pair in req.pairs:
        a = Complex(pair.a.x, pair.a.y)
        b = Complex(pair.b.x, pair.b.y)
        results.append(round(hyperbolic_distance(a, b), 10))
    return {"distances": results}


@app.get("/v1/pricing")
def pricing():
    return {
        "tiers": [
            {
                "name": "Free",
                "price": "$0/mo",
                "limits": "100 requests/day",
                "features": ["Distance computation", "Geodesic paths", "Triangle metrics", "Circle generation"],
            },
            {
                "name": "Pro",
                "price": "$29/mo",
                "limits": "10,000 requests/day",
                "features": [
                    "Everything in Free",
                    "Terrain generation",
                    "Hyperbolic tilings (SVG + JSON)",
                    "Batch operations (up to 1000/call)",
                    "Height map export",
                    "Email support",
                ],
            },
            {
                "name": "Enterprise",
                "price": "$199/mo",
                "limits": "100,000 requests/day",
                "features": [
                    "Everything in Pro",
                    "Dedicated instance",
                    "Custom palettes & tiling params",
                    "Priority support & SLA",
                    "Webhook notifications",
                ],
            },
        ],
        "signup": "https://hyperbolica.dev/signup",
    }
