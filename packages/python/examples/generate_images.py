"""Render a 2D Perlin noise field to an image.

Requires the optional ``images`` dependencies::

    uv run --extra images python examples/generate_images.py
"""

import matplotlib.pyplot as plt
import numpy as np

from noise_algorithms import FractalPerlinNoise2D


def main() -> None:
    width, height = 512, 512
    noise = FractalPerlinNoise2D(
        seed=0,
        frequency=1 / 64,
        octaves=6,
        lacunarity=2.5,
        persistence=0.2,
    )

    image = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            image[y, x] = noise.noise(x, y)

    plt.imshow(image, cmap="gray")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
