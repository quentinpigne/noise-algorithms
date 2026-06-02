"""Integration test: render noise images from the built wheel.

The package is built (``uv build``) and imported from an isolated environment
(``uv run --no-project --with <wheel>``), so this exercises the actual
distributed artifact rather than the working-tree sources. Each rendered image
is compared pixel-for-pixel against a committed snapshot and written to
``tests/output`` for inspection.

Renderings: 1D as a line graph of the signal, 2D as a grayscale field, and 3D as
a montage of z-slices (a grid of tiles sampled at increasing depth).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

SEED = 42
SCALE = 0.03

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PACKAGE_ROOT / "tests" / "snapshots"
OUTPUT_DIR = PACKAGE_ROOT / "tests" / "output"

# (name, width, height, kind)
CASES = [
    ("perlin-noise-1d.png", 512, 256, "1d"),
    ("perlin-noise-2d.png", 256, 256, "2d"),
    ("perlin-noise-3d.png", 256, 256, "3d"),
]

pytestmark = pytest.mark.integration

_PREAMBLE = f"""
import sys
from noise_algorithms import PerlinConfig, perlin_1d, perlin_2d, perlin_3d

config = PerlinConfig(seed={SEED}, scale={SCALE})
W, H = {{width}}, {{height}}
buf = bytearray([255]) * (W * H)


def gray(value):
    return max(0, min(255, int((value + 1) / 2 * 255)))
"""

_BODIES = {
    "1d": """
mid = H // 2
for x in range(W):
    buf[mid * W + x] = 210
prev = None
for x in range(W):
    y = max(0, min(H - 1, round((1 - (perlin_1d(x, config) + 1) / 2) * (H - 1))))
    lo, hi = (y, y) if prev is None else (min(prev, y), max(prev, y))
    for yy in range(lo, hi + 1):
        buf[yy * W + x] = 30
    prev = y
""",
    "2d": """
for y in range(H):
    for x in range(W):
        buf[y * W + x] = gray(perlin_2d(x, y, config))
""",
    # Swiss-cheese cube: sample a voxel grid, keep the densest ~60% solid, draw
    # the exposed faces in isometric projection (painter's order, shaded).
    "3d": """
import math

N, STEP, FILL = 24, 6, 0.6
A, B, C = 4, 2, 4
OX, OY = W / 2, H / 2
TOP, RIGHT, LEFT = 215, 120, 165


def at(i, j, k):
    return (i * N + j) * N + k


vals = [0.0] * (N * N * N)
for i in range(N):
    for j in range(N):
        for k in range(N):
            vals[at(i, j, k)] = perlin_3d(i * STEP, j * STEP, k * STEP, config)
threshold = sorted(vals)[int(FILL * len(vals))]


def solid(i, j, k):
    return 0 <= i < N and 0 <= j < N and 0 <= k < N and vals[at(i, j, k)] <= threshold


def project(i, j, k):
    return (OX + (i - j) * A, OY + (i + j) * B - k * C)


def fill_quad(pts, value):
    ys = [p[1] for p in pts]
    y_min = max(0, int(math.floor(min(ys))))
    y_max = min(H - 1, int(math.ceil(max(ys))))
    for y in range(y_min, y_max + 1):
        xs = []
        for e in range(4):
            x1, y1 = pts[e]
            x2, y2 = pts[(e + 1) % 4]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
        if len(xs) < 2:
            continue
        x_left = max(0, round(min(xs)))
        x_right = min(W - 1, round(max(xs)))
        for x in range(x_left, x_right + 1):
            buf[y * W + x] = value


voxels = [
    (i, j, k)
    for i in range(N)
    for j in range(N)
    for k in range(N)
    if solid(i, j, k)
]
voxels.sort(key=lambda v: v[0] + v[1] + v[2])
for i, j, k in voxels:
    if not solid(i, j + 1, k):
        fill_quad(
            [project(i, j + 1, k), project(i + 1, j + 1, k),
             project(i + 1, j + 1, k + 1), project(i, j + 1, k + 1)], LEFT)
    if not solid(i + 1, j, k):
        fill_quad(
            [project(i + 1, j, k), project(i + 1, j + 1, k),
             project(i + 1, j + 1, k + 1), project(i + 1, j, k + 1)], RIGHT)
    if not solid(i, j, k + 1):
        fill_quad(
            [project(i, j, k + 1), project(i + 1, j, k + 1),
             project(i + 1, j + 1, k + 1), project(i, j + 1, k + 1)], TOP)
""",
}

_EMIT = "\nsys.stdout.buffer.write(bytes(buf))\n"


def _render_script(kind: str, width: int, height: int) -> str:
    return _PREAMBLE.format(width=width, height=height) + _BODIES[kind] + _EMIT


@pytest.fixture(scope="session")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> str:
    if shutil.which("uv") is None:
        pytest.skip("uv is required to build and install the wheel")
    out_dir = tmp_path_factory.mktemp("wheel")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(out_dir)],
        cwd=PACKAGE_ROOT,
        check=True,
        capture_output=True,
    )
    wheels = list(out_dir.glob("*.whl"))
    assert wheels, "no wheel produced by `uv build`"
    return str(wheels[0])


@pytest.mark.parametrize(("name", "width", "height", "kind"), CASES)
def test_perlin_image_matches_snapshot(
    wheel: str, name: str, width: int, height: int, kind: str
) -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--with",
            wheel,
            "python",
            "-c",
            _render_script(kind, width, height),
        ],
        check=True,
        capture_output=True,
    )
    pixels = result.stdout
    assert len(pixels) == width * height, "unexpected rendered byte count"

    generated = Image.frombytes("L", (width, height), pixels)

    # Always write the generated image so it can be inspected / diffed.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated.save(OUTPUT_DIR / name)

    # Refresh the snapshot on demand or on first run.
    snapshot = SNAPSHOT_DIR / name
    if os.environ.get("UPDATE_SNAPSHOTS") or not snapshot.exists():
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        generated.save(snapshot)

    expected = Image.open(snapshot).convert("L")
    assert generated.tobytes() == expected.tobytes(), (
        f"rendered noise does not match {name} "
        f"(generated image written to {OUTPUT_DIR / name})"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
