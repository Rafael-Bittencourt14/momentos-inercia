"""Figuras geométricas elementares (V4).

Convenções:
- Cada figura possui (x, y) como coordenadas do seu centroide no sistema global.
- furo=True significa que a área é subtraída (A < 0) e os momentos próprios também.
- Ix, Iy, Ixy aqui são SEMPRE relativos ao eixo que passa pelo centroide da figura (Ix̄, Iȳ, Ix̄ȳ).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol


class Figura(Protocol):
    nome: str
    x: float
    y: float
    furo: bool

    def area(self) -> float: ...
    def ix_proprio(self) -> float: ...
    def iy_proprio(self) -> float: ...
    def ixy_proprio(self) -> float: ...


def _aplicar_sinal_furo(valor: float, furo: bool) -> float:
    return -valor if furo else valor


@dataclass(frozen=True)
class Retangulo:
    base: float
    altura: float
    x: float = 0.0
    y: float = 0.0
    furo: bool = False
    nome: str = "Retângulo"

    def area(self) -> float:
        return _aplicar_sinal_furo(self.base * self.altura, self.furo)

    def ix_proprio(self) -> float:
        ix = (self.base * self.altura**3) / 12
        return _aplicar_sinal_furo(ix, self.furo)

    def iy_proprio(self) -> float:
        iy = (self.altura * self.base**3) / 12
        return _aplicar_sinal_furo(iy, self.furo)

    def ixy_proprio(self) -> float:
        return 0.0


@dataclass(frozen=True)
class Circulo:
    raio: float
    x: float = 0.0
    y: float = 0.0
    furo: bool = False
    nome: str = "Círculo"

    def area(self) -> float:
        a = math.pi * self.raio**2
        return _aplicar_sinal_furo(a, self.furo)

    def ix_proprio(self) -> float:
        ix = (math.pi * self.raio**4) / 4
        return _aplicar_sinal_furo(ix, self.furo)

    def iy_proprio(self) -> float:
        iy = (math.pi * self.raio**4) / 4
        return _aplicar_sinal_furo(iy, self.furo)

    def ixy_proprio(self) -> float:
        return 0.0


@dataclass(frozen=True)
class TrianguloRetangulo:
    """Triângulo retângulo com catetos paralelos aos eixos.

    Nota didática:
    - O sinal de Ixy próprio depende da orientação do triângulo no plano.
    - Por isso existe o parâmetro sinal_ixy (+1 ou -1).
    """
    base: float
    altura: float
    x: float = 0.0
    y: float = 0.0
    sinal_ixy: int = 1   # +1 ou -1
    furo: bool = False
    nome: str = "Triângulo Retângulo"

    def __post_init__(self):
        if self.sinal_ixy not in (1, -1):
            raise ValueError("sinal_ixy deve ser +1 ou -1.")

    def area(self) -> float:
        a = (self.base * self.altura) / 2
        return _aplicar_sinal_furo(a, self.furo)

    def ix_proprio(self) -> float:
        ix = (self.base * self.altura**3) / 36
        return _aplicar_sinal_furo(ix, self.furo)

    def iy_proprio(self) -> float:
        iy = (self.altura * self.base**3) / 36
        return _aplicar_sinal_furo(iy, self.furo)

    def ixy_proprio(self) -> float:
        ixy = (self.base**2 * self.altura**2) / 72
        ixy = ixy * self.sinal_ixy
        return _aplicar_sinal_furo(ixy, self.furo)


@dataclass(frozen=True)
class Semicirculo:
    raio: float
    x: float = 0.0
    y: float = 0.0
    furo: bool = False
    nome: str = "Semicírculo"

    def area(self) -> float:
        a = (math.pi * self.raio**2) / 2
        return _aplicar_sinal_furo(a, self.furo)

    def ix_proprio(self) -> float:
        # Fórmula tabelada do formulário: 0,1098 * R^4
        ix = 0.1098 * self.raio**4
        return _aplicar_sinal_furo(ix, self.furo)

    def iy_proprio(self) -> float:
        iy = (math.pi * self.raio**4) / 8
        return _aplicar_sinal_furo(iy, self.furo)

    def ixy_proprio(self) -> float:
        return 0.0


@dataclass(frozen=True)
class QuartoCirculo:
    """Quarto de círculo.

    Nota:
    - O sinal de Ixy depende da orientação; por padrão deixamos -1 (caso comum em tabelas).
    """
    raio: float
    x: float = 0.0
    y: float = 0.0
    sinal_ixy: int = -1
    furo: bool = False
    nome: str = "1/4 de Círculo"

    def __post_init__(self):
        if self.sinal_ixy not in (1, -1):
            raise ValueError("sinal_ixy deve ser +1 ou -1.")

    def area(self) -> float:
        a = (math.pi * self.raio**2) / 4
        return _aplicar_sinal_furo(a, self.furo)

    def ix_proprio(self) -> float:
        ix = 0.0549 * self.raio**4
        return _aplicar_sinal_furo(ix, self.furo)

    def iy_proprio(self) -> float:
        iy = 0.0549 * self.raio**4
        return _aplicar_sinal_furo(iy, self.furo)

    def ixy_proprio(self) -> float:
        ixy = 0.01647 * self.raio**4
        ixy = ixy * self.sinal_ixy
        return _aplicar_sinal_furo(ixy, self.furo)
