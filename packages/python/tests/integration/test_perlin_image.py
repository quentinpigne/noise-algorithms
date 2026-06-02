"""Integration test: render a noise image from the built wheel.

The package is built (``uv build``) and imported from an isolated environment
(``uv run --no-project --with <wheel>``), so this exercises the actual
distributed artifact rather than the working-tree sources. The rendered image is
compared pixel-for-pixel against a committed snapshot and written to
``tests/output`` for inspection.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

WIDTH = 256
HEIGHT = 256
SEED = 42
SCALE = 0.03

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = PACKAGE_ROOT / "tests" / "snapshots" / "perlin-noise-2d.png"
OUTPUT_DIR = PACKAGE_ROOT / "tests" / "output"
OUTPUT = OUTPUT_DIR / "perlin-noise-2d.png"

# Script run inside the isolated environment; emits raw grayscale bytes (one per
# pixel) on stdout so the test process needs no extra deps in that environment.
_RENDER_SCRIPT = f"""
import sys
from noise_algorithms import PerlinConfig, perlin_2d

config = PerlinConfig(seed={SEED}, scale={SCALE})
buf = bytearray({WIDTH} * {HEIGHT})
for y in range({HEIGHT}):
    for x in range({WIDTH}):
        value = perlin_2d(x, y, config)
        buf[y * {WIDTH} + x] = max(0, min(255, int((value + 1) / 2 * 255)))
sys.stdout.buffer.write(bytes(buf))
"""

pytestmark = pytest.mark.integration


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


def test_perlin_image_matches_snapshot(wheel: str) -> None:
    result = subprocess.run(
        ["uv", "run", "--no-project", "--with", wheel, "python", "-c", _RENDER_SCRIPT],
        check=True,
        capture_output=True,
    )
    pixels = result.stdout
    assert len(pixels) == WIDTH * HEIGHT, "unexpected rendered byte count"

    generated = Image.frombytes("L", (WIDTH, HEIGHT), pixels)

    # Always write the generated image so it can be inspected / diffed.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated.save(OUTPUT)

    # Refresh the snapshot on demand or on first run.
    if os.environ.get("UPDATE_SNAPSHOTS") or not SNAPSHOT.exists():
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        generated.save(SNAPSHOT)

    snapshot = Image.open(SNAPSHOT).convert("L")
    assert generated.tobytes() == snapshot.tobytes(), (
        "rendered noise does not match the committed snapshot "
        f"(generated image written to {OUTPUT})"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
