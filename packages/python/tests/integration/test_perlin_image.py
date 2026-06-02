"""Integration test: render noise images from the built wheel.

The package is built (``uv build``) and imported from an isolated environment
(``uv run --no-project --with <wheel>``), so this exercises the actual
distributed artifact rather than the working-tree sources. Each rendered image
is compared pixel-for-pixel against a committed snapshot and written to
``tests/output`` for inspection.
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

# (name, width, height, noise expression evaluated for each (x, y))
CASES = [
    ("perlin-noise-1d.png", 256, 64, "perlin_1d(x, config)"),
    ("perlin-noise-2d.png", 256, 256, "perlin_2d(x, y, config)"),
    ("perlin-noise-3d.png", 256, 256, "perlin_3d(x, y, 0, config)"),
]

pytestmark = pytest.mark.integration


def _render_script(width: int, height: int, expression: str) -> str:
    """Script run inside the isolated env; emits raw grayscale bytes on stdout."""
    return f"""
import sys
from noise_algorithms import PerlinConfig, perlin_1d, perlin_2d, perlin_3d

config = PerlinConfig(seed={SEED}, scale={SCALE})
buf = bytearray({width} * {height})
for y in range({height}):
    for x in range({width}):
        value = {expression}
        buf[y * {width} + x] = max(0, min(255, int((value + 1) / 2 * 255)))
sys.stdout.buffer.write(bytes(buf))
"""


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


@pytest.mark.parametrize(("name", "width", "height", "expression"), CASES)
def test_perlin_image_matches_snapshot(
    wheel: str, name: str, width: int, height: int, expression: str
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
            _render_script(width, height, expression),
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
