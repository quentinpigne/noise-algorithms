"""Internal interpolation helpers shared by the noise generators."""

from __future__ import annotations


def fade(t: float) -> float:
    """Perlin's smoothing function ``6t^5 - 15t^4 + 10t^3``."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between ``a`` and ``b`` by ``t``."""
    return a + t * (b - a)
