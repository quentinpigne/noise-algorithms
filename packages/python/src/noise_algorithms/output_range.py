"""Remap noise output to a different range."""


def to_unit_range(value: float) -> float:
    """Remap a noise value from the signed range ``[-1, 1]`` to the unit range
    ``[0, 1]`` — handy for grayscale images, textures or heightmaps.

    Noise generators always output ``[-1, 1]``; apply this to a value (or map it
    over a sampled line/grid/volume) when you need ``[0, 1]`` instead.
    """
    return (value + 1) / 2
