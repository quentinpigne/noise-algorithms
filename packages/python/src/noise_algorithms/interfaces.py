"""Structural-typing protocols describing the noise generators' contract.

These mirror the TypeScript ``NoiseGenerator{1,2,3}D`` and
``FractalNoiseGenerator{1,2,3}D`` interfaces: any object exposing a matching
``noise`` method satisfies them (structural typing), so user code can be written
against the protocol rather than a concrete class. A fractal generator is still
a noise generator (it is sampled the same way), so the fractal protocols extend
the plain ones.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class NoiseGenerator1D(Protocol):
    def noise(self, x: float) -> float: ...


@runtime_checkable
class NoiseGenerator2D(Protocol):
    def noise(self, x: float, y: float) -> float: ...


@runtime_checkable
class NoiseGenerator3D(Protocol):
    def noise(self, x: float, y: float, z: float) -> float: ...


@runtime_checkable
class FractalNoiseGenerator1D(NoiseGenerator1D, Protocol):
    def noise(self, x: float) -> float: ...


@runtime_checkable
class FractalNoiseGenerator2D(NoiseGenerator2D, Protocol):
    def noise(self, x: float, y: float) -> float: ...


@runtime_checkable
class FractalNoiseGenerator3D(NoiseGenerator3D, Protocol):
    def noise(self, x: float, y: float, z: float) -> float: ...
