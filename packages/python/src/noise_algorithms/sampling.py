"""Sample noise generators over a regular region.

These helpers turn a per-coordinate noise generator into a sequence of values
over an interval (a curve), a grid (an image), or a volume. They depend only on
the ``NoiseGenerator{1,2,3}D`` protocol, so they work with any generator —
single-octave or fractal, Perlin or a future algorithm.
"""

from .interfaces import NoiseGenerator1D, NoiseGenerator2D, NoiseGenerator3D


def sample_line(
    generator: NoiseGenerator1D,
    *,
    count: int,
    start: float = 0.0,
    step: float = 1.0,
) -> list[float]:
    """Sample a 1D generator over a regular interval — e.g. a curve.

    The i-th sample is taken at ``start + i * step``. Returns ``count`` values,
    each in ``[-1, 1]``.
    """
    return [generator.noise(start + i * step) for i in range(count)]


def sample_grid(
    generator: NoiseGenerator2D,
    *,
    width: int,
    height: int,
    start_x: float = 0.0,
    start_y: float = 0.0,
    step: float = 1.0,
) -> list[list[float]]:
    """Sample a 2D generator over a regular grid — e.g. an image.

    The sample at column ``x``, row ``y`` is taken at
    ``(start_x + x * step, start_y + y * step)``. Returns a ``height × width``
    nested list indexed as ``grid[y][x]``, values in ``[-1, 1]``.
    """
    return [
        [generator.noise(start_x + x * step, start_y + y * step) for x in range(width)]
        for y in range(height)
    ]


def sample_volume(
    generator: NoiseGenerator3D,
    *,
    width: int,
    height: int,
    depth: int,
    start_x: float = 0.0,
    start_y: float = 0.0,
    start_z: float = 0.0,
    step: float = 1.0,
) -> list[list[list[float]]]:
    """Sample a 3D generator over a regular volume.

    The sample at ``(x, y, z)`` is taken at
    ``(start_x + x * step, start_y + y * step, start_z + z * step)``. Returns a
    ``depth × height × width`` nested list indexed as ``volume[z][y][x]``, values
    in ``[-1, 1]``.
    """
    return [
        [
            [
                generator.noise(
                    start_x + x * step, start_y + y * step, start_z + z * step
                )
                for x in range(width)
            ]
            for y in range(height)
        ]
        for z in range(depth)
    ]
