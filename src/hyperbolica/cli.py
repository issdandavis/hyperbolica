from __future__ import annotations

import argparse
from typing import Sequence

from .poincare import poincare_distance


def _parse_vector(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def cmd_dist(u: Sequence[float], v: Sequence[float]) -> int:
    print(f"{poincare_distance(u, v):.12g}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="hyperbolica")
    sub = parser.add_subparsers(dest="command", required=True)

    dist = sub.add_parser("dist", help="compute Poincare distance")
    dist.add_argument("--u", required=True, help="comma-separated vector")
    dist.add_argument("--v", required=True, help="comma-separated vector")

    args = parser.parse_args()
    if args.command == "dist":
        return cmd_dist(_parse_vector(args.u), _parse_vector(args.v))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
