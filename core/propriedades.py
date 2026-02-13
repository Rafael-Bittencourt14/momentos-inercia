"""Modelos de dados para resultados."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class ResultadosSecao:
    unidade_comprimento: str

    area_total: float
    xg: float
    yg: float

    ix: float
    iy: float
    ixy: float

    i1: float
    i2: float
    alpha1_rad: float
    alpha2_rad: float

    # Espaço para expansão futura (Wx, Wy, raio de giração, etc.)
    extras: Optional[Dict[str, Any]] = None

    def como_dict(self) -> Dict[str, Any]:
        return {
            "unidade_comprimento": self.unidade_comprimento,
            "area_total": self.area_total,
            "xg": self.xg,
            "yg": self.yg,
            "ix": self.ix,
            "iy": self.iy,
            "ixy": self.ixy,
            "i1": self.i1,
            "i2": self.i2,
            "alpha1_rad": self.alpha1_rad,
            "alpha2_rad": self.alpha2_rad,
            "extras": self.extras or {},
        }
