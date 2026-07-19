# Perlin Noise — How it works, and how this library implements it

This document explains Perlin noise from the ground up — first the intuition and
the math in 1D, 2D, 3D, then the generalization to N dimensions — and finally
how the [`noise-algorithms`](../README.md) packages implement it.

> Notation: `floor(x)` is the largest integer ≤ `x`, and the *fractional part*
> is `frac(x) = x - floor(x)`, always in `[0, 1)`.

---

## 1. What is Perlin noise?

Perlin noise (Ken Perlin, 1983) is a **gradient noise**: a function that maps a
point in space to a single value, with three defining properties.

- **Coherent / smooth** — nearby inputs give nearby outputs (no white-noise
  hash); the field looks like soft hills and valleys.
- **Deterministic** — fully determined by a `seed`; the same seed always
  produces the same field.
- **Bounded** — outputs land in (approximately) `[-1, 1]`.

It is the workhorse behind procedural textures, terrain heightmaps, clouds,
flow fields, and looping animations.

**Gradient vs value noise.** *Value* noise assigns a random *value* to each grid
point and interpolates the values. *Gradient* (Perlin) noise assigns a random
*direction* (a gradient vector) to each grid point, and the value at a point
comes from **dot products** of those gradients with the offsets to the point.
Gradient noise looks visually richer and avoids the "blocky" axis-aligned
artifacts value noise tends to show.

---

## 2. The core idea

Lay an **integer grid** over space. The point you query falls inside one grid
**cell** (a segment in 1D, a square in 2D, a cube in 3D). The noise value is
built from the cell's **corners**:

1. **A pseudo-random gradient** is attached to each corner (chosen
   deterministically from the corner's integer coordinates via a hash).
2. **Each corner contributes** the dot product of its gradient with the vector
   pointing *from that corner to the query point* (the "displacement").
3. **The contributions are blended** with a smooth interpolation, weighted by
   how close the point is to each corner along every axis.

So Perlin noise needs four ingredients, each covered below:

| Ingredient | Role |
| --- | --- |
| Grid + cell | locate the point and its surrounding corners |
| Permutation table | hash a corner's coordinates → a gradient choice |
| Gradient · displacement | each corner's contribution |
| Fade + lerp | smoothly blend the corner contributions |

---

## 3. The building blocks

### 3.1 The permutation table (hashing)

We need a cheap, deterministic way to turn integer corner coordinates into a
"random" gradient choice. Perlin's trick: a **permutation table** — the integers
`0..255` shuffled by the seed — used as a hash.

```python
# _permutation.py
def build_permutation(seed: int) -> tuple[int, ...]:
    values = list(range(256))
    random.Random(seed).shuffle(values)
    return tuple(values + values)   # 512 entries: the 256 values, duplicated
```

To hash several coordinates, the table is applied repeatedly and the
coordinates are folded in one axis at a time (see §4–§7).

**Why duplicate the table to 512 entries?** When folding, we compute
`perm[h + cell]` where both `h` and `cell` are in `0..255`, so the sum can reach
`510`. Duplicating the table means that index is always valid **without masking
the sum** — only the cell coordinates themselves are masked with `& 255` (which
also makes the field tile every 256 cells).

### 3.2 The fade curve

If we blended corners with plain linear interpolation, the result would have
visible creases at cell boundaries (the slope changes abruptly). Perlin's
**fade** (a.k.a. *smootherstep*) reshapes the interpolation weight `t ∈ [0, 1]`:

```
fade(t) = 6t⁵ − 15t⁴ + 10t³
```

```python
# _interpolation.py
def fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)
```

Its first **and** second derivatives are zero at `t = 0` and `t = 1`. That makes
the field `C²`-continuous across cell borders — no creases. (Perlin's original
1985 paper used `3t² − 2t³`, which only zeroes the first derivative; the quintic
above is the 2002 "improved noise" upgrade.)

### 3.3 Linear interpolation (lerp)

```
lerp(a, b, t) = a + t · (b − a)
```

Used to combine two values; the weight `t` we feed it is always a *faded*
fraction.

---

## 4. Perlin noise in 1D

The "grid" is just the integer number line; a point `x` sits in the cell
`[x0, x0+1]`.

```
        x0            x        x0+1
         |------------*----------|
         |<--- xf --->|
   gradient g0                 gradient g1
```

**Step 1 — locate the cell.**
```
x0 = floor(x) & 255      # left corner (masked into 0..255)
x1 = (x0 + 1) & 255      # right corner
xf = frac(x)             # how far into the cell, in [0, 1)
```

**Step 2 — hash each corner to a gradient.** In 1D a "gradient" is just a sign,
`+1` or `−1`, taken from the parity of the hashed corner:
```
h0 = perm[perm[x0]]      g0 = +1 if h0 even else −1
h1 = perm[perm[x1]]      g1 = +1 if h1 even else −1
```

**Step 3 — corner contributions** = gradient × displacement. The displacement
from the left corner is `xf`; from the right corner it is `xf − 1` (negative,
since the point is to its left):
```
n0 = g0 · (xf)
n1 = g1 · (xf − 1)
```

**Step 4 — blend** with the faded fraction:
```
u = fade(xf)
value = lerp(n0, n1, u)
```

That single value is one octave of 1D Perlin noise. Because each `n` is a
sign × a number in `[-1, 1]`, the blended result also lands in `[-1, 1]`.

---

## 5. Perlin noise in 2D

Now the cell is a **unit square** with **4 corners**. Everything from 1D repeats
per axis, and the gradients become 2D vectors.

```
   (x0,y1) o-------------o (x1,y1)
           |             |
           |      * (x,y)|
           |             |
   (x0,y0) o-------------o (x1,y0)
```

**Step 1 — locate the cell**, per axis:
```
x0, x1 = floor(x)&255, (x0+1)&255      xf = frac(x)
y0, y1 = floor(y)&255, (y0+1)&255      yf = frac(y)
```

**Step 2 — hash the 4 corners.** The hash folds the two coordinates through the
table:
```
hash(cx, cy) = perm[ perm[ perm[cx] + cy ] ]
```
giving `h00, h01, h10, h11` for the four `(cx, cy)` combinations.

**Step 3 — gradients & contributions.** Each hash selects one of **8 gradient
directions** (the 4 diagonals of length 1 plus the 4 axis directions), via
`h & 7`. The contribution is the dot product of that gradient with the
displacement from the corner:

```
gradients = [(±u, ±u), (0, ±1), (±1, 0)]   with u = 1/√2

n00 = grad(h00) · (xf,     yf)
n10 = grad(h10) · (xf − 1, yf)
n01 = grad(h01) · (xf,     yf − 1)
n11 = grad(h11) · (xf − 1, yf − 1)
```

**Step 4 — blend along each axis.** First interpolate along x (weight
`u = fade(xf)`), then along y (weight `v = fade(yf)`):
```
nx0 = lerp(n00, n10, u)      # bottom edge
nx1 = lerp(n01, n11, u)      # top edge
value = lerp(nx0, nx1, v)
```

---

## 6. Perlin noise in 3D

The cell is a **cube** with **8 corners**. Same recipe, one more axis.

- **Locate**: `x0/x1, y0/y1, z0/z1` and `xf, yf, zf`.
- **Hash** folds three coordinates: `perm[perm[perm[perm[cx]+cy]+cz]]`.
- **Gradients**: **12 vectors** pointing to the midpoints of the cube's edges,
  selected with `h % 12`. The contribution is again `gradient · displacement`,
  with displacements like `(xf−1, yf, zf−1)` for the 8 corners.
- **Blend**: interpolate the 8 contributions along x (4 lerps), then the 4
  results along y (2 lerps), then those along z (1 lerp) — a *trilinear* blend
  with faded weights `u, v, w`.

---

## 7. Generalizing to N dimensions

Look at 1D → 2D → 3D and three patterns emerge. They are *the whole algorithm*,
parameterized by the number of axes `n`:

1. **The cell has `2ⁿ` corners** — a segment (2), a square (4), a cube (8), a
   tesseract (16), … Each corner is a choice of offset `0` or `1` **per axis**.
   A choice of `n` bits is exactly an integer `0 .. 2ⁿ−1`, so we enumerate
   corners with a loop and read each axis's offset from a bit:

   ```
   offset along axis = (corner >> axis) & 1
   ```

   | `corner` (2D) | bits | offsets (x, y) |
   | :-: | :-: | :-: |
   | 0 | `00` | (0, 0) |
   | 1 | `01` | (1, 0) |
   | 2 | `10` | (0, 1) |
   | 3 | `11` | (1, 1) |

2. **Hashing is a fold** over the axes — start from the first coordinate, then
   for every further axis "add the coordinate and re-hash":

   ```
   h = perm[c₀]
   for axis in 1 .. n−1:   h = perm[h + cₐₓᵢₛ]
   h = perm[h]
   ```

   This reproduces `perm[perm[c₀]]` (1D), `perm[perm[perm[c₀]+c₁]]` (2D),
   `perm[perm[perm[perm[c₀]+c₁]+c₂]]` (3D), … exactly.

3. **Blending is a pairwise reduction**, one axis at a time. With the `2ⁿ`
   contributions in an array, lerp adjacent pairs using `fade(fracₐₓᵢₛ)` —
   halving the array each pass — until a single value remains:

   ```
   2ⁿ  →(axis 0)→  2ⁿ⁻¹  →(axis 1)→  …  →(axis n−1)→  1
   ```

The **only** part that stays dimension-specific is the **gradient set** (±1 in
1D, 8 vectors in 2D, 12 in 3D). Everything else — corners, hashing, blending —
is identical for every `n`.

---

## 8. Fractal noise (fBm / octaves)

A single octave looks smooth but a bit plain. Real textures stack several
octaves of noise at increasing frequency and decreasing amplitude — *fractional
Brownian motion* (fBm):

```
value = Σ  octave(point · frequencyᵢ) · amplitudeᵢ
        i

frequency starts at `frequency` and is multiplied by lacunarity  each octave
amplitude starts at 1           and is multiplied by persistence each octave
```

The sum is divided by the total amplitude to keep the result in `[-1, 1]`.

Fractal layering is independent of the underlying noise function, so in this
library it is a **separate abstract concept** — the octave loop lives once in the
abstract `FractalNoiseGenerator`, reused by every algorithm's fractal variant,
rather than baked into Perlin (see §9). The `seed` below belongs to the noise
source; the rest are the fractal layer's parameters.

| Parameter | Meaning |
| --- | --- |
| `seed` | Chooses the permutation table (the field) of the noise source. |
| `frequency` | Base frequency applied to the input coordinates of the first octave (zoom). |
| `octaves` | How many layers are summed. |
| `lacunarity` | Frequency multiplier between octaves (usually `2`). |
| `persistence` | Amplitude multiplier between octaves (usually `0.5`). |

---

## 9. How this library implements it

The implementation mirrors the structure above. The **engine is
dimension-agnostic** and lives in a shared base class; each dimension only
supplies its **gradient strategy**. The Python and TypeScript packages share the
same design.

### 9.1 File map (Python)

Two abstract concepts anchor the design: **`NoiseGenerator`** (generate noise)
and **`FractalNoiseGenerator`** (combine octaves of noise), each declined into
three dimension interfaces. Perlin is the one implementation so far, in a
single-octave and a fractal flavour.

| Concept (above) | File / symbol |
| --- | --- |
| Permutation table (§3.1) | `_permutation.py` → `build_permutation(seed)` |
| Fade & lerp (§3.2–3.3) | `_interpolation.py` → `fade`, `lerp` |
| Abstract concept: generate noise | `noise_generator.py` → `NoiseGenerator` |
| Abstract concept: combine into fractal noise (§8) | `fractal_noise_generator.py` → `FractalNoiseGenerator` |
| Dimension interfaces | `interfaces.py` → `NoiseGenerator{1,2,3}D`, `FractalNoiseGenerator{1,2,3}D` protocols |
| Single-octave engine (§4–§7) | `perlin/_base.py` → `PerlinNoise(NoiseGenerator)` |
| Gradient strategy (§4–§6) | `perlin/perlin_{1,2,3}d.py` → `_gradient` |
| Perlin single octave | `perlin/perlin_{1,2,3}d.py` → `PerlinNoise{1,2,3}D`, `perlin_{1,2,3}d` |
| Perlin fractal | `perlin/perlin_{1,2,3}d.py` → `FractalPerlinNoise{1,2,3}D(FractalNoiseGenerator)`, `fractal_perlin_{1,2,3}d` |

### 9.2 The dimension-agnostic octave

The single octave (`PerlinNoise._octave`) is exactly §7 in code:

```python
def _octave(self, *coords: float) -> float:
    permutation = self._permutation
    n = len(coords)

    floors = [math.floor(c) for c in coords]
    cells = [f & 255 for f in floors]                       # §4 step 1, per axis
    fracs = [c - f for c, f in zip(coords, floors, strict=True)]
    faded = [fade(f) for f in fracs]

    values = []
    for corner in range(1 << n):                            # §7 pattern 1: 2ⁿ corners
        h = permutation[(cells[0] + (corner & 1)) & 255]    # §7 pattern 2: hash fold
        for axis in range(1, n):
            h = permutation[h + ((cells[axis] + ((corner >> axis) & 1)) & 255)]
        h = permutation[h]

        displacement = [fracs[axis] - ((corner >> axis) & 1) for axis in range(n)]
        values.append(self._gradient(h, displacement))      # dimension-specific

    for axis in range(n):                                   # §7 pattern 3: reduction
        values = [
            lerp(values[i], values[i + 1], faded[axis])
            for i in range(0, len(values), 2)
        ]
    return values[0]
```

The public `noise(...)` of a Perlin generator returns exactly this single
octave. The octave summation of §8 lives separately in
`FractalNoiseGenerator._fractal` (§9.4).

### 9.3 The per-dimension gradient

A subclass is now tiny — it only declares its arity and its gradient set. For
example, 2D:

```python
class PerlinNoise2D(PerlinNoise):
    def noise(self, x: float, y: float) -> float:
        return self._octave(x, y)

    def _gradient(self, h: int, displacement: list[float]) -> float:
        gx, gy = _GRADIENTS[h & 7]          # 8 directions, picked by the hash
        return displacement[0] * gx + displacement[1] * gy
```

1D returns `±displacement[0]` (sign from `h & 1`); 3D dots a 12-vector table
chosen with `h % 12`.

### 9.4 Fractal layering is a second abstract concept

Because fBm is independent of the noise function, the octave summation of §8 is
implemented once in the abstract `FractalNoiseGenerator`
(`fractal_noise_generator.py`), which any source satisfying
`NoiseGenerator{1,2,3}D` can feed. This is a **layering technique, not a noise
algorithm** — the base is abstract (you cannot instantiate a generic combiner),
so future algorithms (Simplex, Worley, …) reuse the exact same machinery while
"fractal" only ever appears in the public API as a qualifier on a real algorithm.

Each algorithm exposes **four public entry points per dimension** — a class and
a one-shot function, in single-octave and fractal flavours:

| | Class | Function |
| --- | --- | --- |
| Single octave | `PerlinNoise2D` | `perlin_2d(x, y, *, seed=0)` |
| Fractal (fBm) | `FractalPerlinNoise2D` | `fractal_perlin_2d(x, y, *, seed=0, …)` |

```python
from noise_algorithms import FractalPerlinNoise2D

FractalPerlinNoise2D(seed=42, frequency=0.05, octaves=6).noise(12, 7)
```

`FractalPerlinNoise2D` extends `FractalNoiseGenerator` (binding a `PerlinNoise2D`
source), and its `noise` calls `self._fractal(x, y)` — the §8 loop that samples the wrapped
`PerlinNoise2D` source at each octave.

### 9.5 TypeScript parity

The TypeScript package (`packages/typescript`) uses the same architecture and
the same two abstract concepts: `NoiseGenerator` (`src/noise-generator.ts`) and
`FractalNoiseGenerator` (`src/fractal-noise-generator.ts`), each with three
dimension interfaces under `src/interfaces/`. `PerlinNoise1D/2D/3D` implement the
single-octave side; `FractalPerlinNoise1D/2D/3D` extend `FractalNoiseGenerator`
for the fractal side.

The **public API is homogeneous across both packages** — the same four entry
points per dimension, differing only by each language's casing convention:

| Entry point | TypeScript | Python |
| --- | --- | --- |
| Single-octave class | `PerlinNoise2D` | `PerlinNoise2D` |
| Single-octave function | `perlin2D(x, y, options?)` | `perlin_2d(x, y, *, seed=0)` |
| Fractal class | `FractalPerlinNoise2D` | `FractalPerlinNoise2D` |
| Fractal function | `fractalPerlin2D(x, y, options?)` | `fractal_perlin_2d(x, y, …)` |

The remaining differences are idiomatic: TS takes a single options object
(`new FractalPerlinNoise2D({ octaves, frequency, … })`) while Python uses
keyword-only arguments. Every parameter is optional and named, so new ones can
be added without breaking existing call sites.

> **Cross-language note.** Both packages build the permutation table with the
> same portable PRNG — a 32-bit **xorshift32** (`utils/seeded-random.ts` /
> `_seeded_random.py`) driving a Fisher-Yates shuffle with an integer-modulo
> index. It uses only masked 32-bit integer ops, so it is bit-identical in every
> language: **the same seed produces the same field** in Python and TypeScript.
> A set of shared conformance vectors in both test suites guards against drift.
> The default seed is `0` in both.

---

## 10. Further reading

- Ken Perlin, *An Image Synthesizer* (1985) — the original.
- Ken Perlin, *Improving Noise* (2002) — the quintic fade and the 3D gradient set.
- [Perlin noise — Wikipedia](https://en.wikipedia.org/wiki/Perlin_noise)
