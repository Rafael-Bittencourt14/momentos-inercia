from __future__ import annotations

import math
from typing import Any, Dict, Tuple

from core.figuras import (
    Retangulo,
    Circulo,
    TrianguloRetangulo,
    Semicirculo,
    QuartoCirculo,
)

# deslocamento do centróide em relação:
# - ao diâmetro (semicírculo)
# - ao canto (1/4 círculo)
_C = 4.0 / (3.0 * math.pi)  # ~0.424413...


# =========================
# Orientações (V2.1)
# =========================
# Triângulo retângulo e 1/4 de círculo: quadrantes em relação ao ponto de referência (x0,y0)
# NE: +x,+y | NW: -x,+y | SW: -x,-y | SE: +x,-y
ORIENT_Q = {
    "NE ( +x, +y )": (+1, +1),
    "NW ( -x, +y )": (-1, +1),
    "SW ( -x, -y )": (-1, -1),
    "SE ( +x, -y )": (+1, -1),
}

# Semicírculo: direção do arco em relação à linha do diâmetro
# (x0,y0) é o ponto médio do diâmetro
# - diametro "H": horizontal (esquerda-direita)
# - diametro "V": vertical   (baixo-cima)
ORIENT_SEMI = {
    "Cima (arco +y)": ("H", +1),
    "Baixo (arco -y)": ("H", -1),
    "Direita (arco +x)": ("V", +1),
    "Esquerda (arco -x)": ("V", -1),
}


def orient_sx_sy(fig: Dict[str, Any]) -> Tuple[int, int]:
    """Retorna (sx,sy) para figuras com quadrantes (triângulo e 1/4 círculo)."""
    ori = fig.get("orientacao") or "NE ( +x, +y )"
    return ORIENT_Q.get(ori, (+1, +1))


def orient_semi(fig: Dict[str, Any]) -> Tuple[str, int]:
    """Retorna (diametro, sinal) para semicírculo."""
    ori = fig.get("orientacao") or "Cima (arco +y)"
    return ORIENT_SEMI.get(ori, ("H", +1))


def sinal_ixy_por_orientacao(sx: int, sy: int, base_sinal: int = -1) -> int:
    """O produto de inércia (Ixy) muda de sinal quando espelha uma única vez (em x OU em y).

    - sx=-1 espelha em x (flip horizontal)
    - sy=-1 espelha em y (flip vertical)

    Paridade de flips define se troca sinal.
    """
    flips = (1 if sx == -1 else 0) + (1 if sy == -1 else 0)
    return base_sinal if (flips % 2 == 0) else -base_sinal


# =========================
# Centroide (posição)
# =========================
def centroid_xy(fig: Dict[str, Any]) -> Tuple[float, float]:
    """Obtém (x,y) do centróide conforme modo de posicionamento escolhido na UI."""
    tipo = fig["tipo"]
    modo = fig.get("modo_pos", "Centroide (x, y)")

    if modo.startswith("Centroide"):
        return float(fig.get("x", 0.0)), float(fig.get("y", 0.0))

    # modos por referência
    if tipo == "Retângulo":
        b = float(fig["base"])
        h = float(fig["altura"])
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])
        vert = fig.get("vertice", "Inferior esquerdo")

        dx, dy = b / 2.0, h / 2.0
        if vert == "Inferior esquerdo":
            return x0 + dx, y0 + dy
        if vert == "Inferior direito":
            return x0 - dx, y0 + dy
        if vert == "Superior esquerdo":
            return x0 + dx, y0 - dy
        return x0 - dx, y0 - dy  # Superior direito

    if tipo == "Triângulo Retângulo":
        b = float(fig["base"])
        h = float(fig["altura"])
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])
        sx, sy = orient_sx_sy(fig)
        return x0 + sx * (b / 3.0), y0 + sy * (h / 3.0)

    if tipo == "Semicírculo":
        r = float(fig["raio"])
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])
        diam, s = orient_semi(fig)

        if diam == "H":
            return x0, y0 + s * _C * r
        # diam == "V"
        return x0 + s * _C * r, y0

    if tipo == "Quarto de Círculo":
        r = float(fig["raio"])
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])
        sx, sy = orient_sx_sy(fig)
        return x0 + sx * _C * r, y0 + sy * _C * r

    # fallback
    return float(fig.get("x", 0.0)), float(fig.get("y", 0.0))


# =========================
# Dict -> Core
# =========================
def dict_to_core(fig: Dict[str, Any]):
    """Transforma o dict da UI em objeto do core."""
    tipo = fig["tipo"]
    furo = bool(fig.get("furo", False))
    x, y = centroid_xy(fig)

    if tipo == "Retângulo":
        return Retangulo(base=float(fig["base"]), altura=float(fig["altura"]), x=x, y=y, furo=furo)

    if tipo == "Círculo":
        return Circulo(raio=float(fig["raio"]), x=x, y=y, furo=furo)

    if tipo == "Triângulo Retângulo":
        sx, sy = orient_sx_sy(fig)
        sinal = sinal_ixy_por_orientacao(sx, sy, base_sinal=-1)
        return TrianguloRetangulo(
            base=float(fig["base"]),
            altura=float(fig["altura"]),
            x=x,
            y=y,
            sinal_ixy=sinal,
            furo=furo,
        )

    if tipo == "Semicírculo":
        return Semicirculo(raio=float(fig["raio"]), x=x, y=y, furo=furo)

    if tipo == "Quarto de Círculo":
        sx, sy = orient_sx_sy(fig)
        sinal = sinal_ixy_por_orientacao(sx, sy, base_sinal=-1)
        return QuartoCirculo(
            raio=float(fig["raio"]),
            x=x,
            y=y,
            sinal_ixy=sinal,
            furo=furo,
        )

    raise ValueError(f"Tipo não suportado: {tipo}")


# =========================
# Defaults
# =========================
def defaults_for(tipo: str, fid: int) -> Dict[str, Any]:
    """Defaults de cada figura ao clicar no botão +."""
    if tipo == "Retângulo":
        return {
            "id": fid, "tipo": tipo, "furo": False,
            "base": 10.0, "altura": 2.0,
            "modo_pos": "Centroide (x, y)", "x": 0.0, "y": 0.0,
            "x0": 0.0, "y0": 0.0, "vertice": "Inferior esquerdo",
        }

    if tipo == "Círculo":
        return {
            "id": fid, "tipo": tipo, "furo": False,
            "raio": 2.0,
            "modo_pos": "Centroide (x, y)", "x": 0.0, "y": 0.0,
        }

    if tipo == "Triângulo Retângulo":
        return {
            "id": fid, "tipo": tipo, "furo": False,
            "base": 6.0, "altura": 4.0,
            "modo_pos": "Centroide (x, y)", "x": 0.0, "y": 0.0,
            "x0": 0.0, "y0": 0.0,
            "orientacao": "NE ( +x, +y )",
        }

    if tipo == "Semicírculo":
        return {
            "id": fid, "tipo": tipo, "furo": False,
            "raio": 3.0,
            "modo_pos": "Centroide (x, y)", "x": 0.0, "y": 0.0,
            "x0": 0.0, "y0": 0.0,
            "orientacao": "Cima (arco +y)",
        }

    if tipo == "Quarto de Círculo":
        return {
            "id": fid, "tipo": tipo, "furo": False,
            "raio": 3.0,
            "modo_pos": "Centroide (x, y)", "x": 0.0, "y": 0.0,
            "x0": 0.0, "y0": 0.0,
            "orientacao": "NE ( +x, +y )",
        }

    raise ValueError(f"Tipo sem defaults: {tipo}")
