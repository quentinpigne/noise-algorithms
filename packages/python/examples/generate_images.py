"""Render a 2D Perlin noise field to an image.

Requires the optional ``images`` dependencies::

    uv run --extra images python examples/generate_images.py
"""

import matplotlib.pyplot as plt
import numpy as np

from noise_algorithms import fractal_perlin_grid


def main() -> None:
    image = np.array(
        fractal_perlin_grid(
            width=512,
            height=512,
            seed=0,
            frequency=1 / 64,
            octaves=6,
            lacunarity=2.5,
            persistence=0.2,
        )
    )

    plt.imshow(image, cmap="gray")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
