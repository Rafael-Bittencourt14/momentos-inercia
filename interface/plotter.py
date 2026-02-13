from __future__ import annotations

import math
from typing import Dict, List, Tuple, Optional

import plotly.graph_objects as go

from .adapters import centroid_xy, orient_sx_sy, orient_semi

_C = 4.0 / (3.0 * math.pi)


def _bounds_update(xs: List[float], ys: List[float], pts: List[Tuple[float, float]]) -> None:
    for x, y in pts:
        xs.append(x)
        ys.append(y)


def _tri_points(fig: Dict, n_close: bool = True) -> List[Tuple[float, float]]:
    b = float(fig["base"])
    h = float(fig["altura"])
    modo = fig.get("modo_pos", "Centroide (x, y)")
    sx, sy = orient_sx_sy(fig)

    if modo.startswith("Centroide"):
        x, y = centroid_xy(fig)
        x0 = x - sx * (b / 3.0)
        y0 = y - sy * (h / 3.0)
    else:
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])

    pts = [(x0, y0), (x0 + sx * b, y0), (x0, y0 + sy * h)]
    if n_close:
        pts.append((x0, y0))
    return pts


def _semi_poly(fig: Dict, n: int = 60) -> List[Tuple[float, float]]:
    r = float(fig["raio"])
    modo = fig.get("modo_pos", "Centroide (x, y)")
    diam, s = orient_semi(fig)

    if modo.startswith("Centroide"):
        x, y = centroid_xy(fig)
        if diam == "H":
            x0 = x
            y0 = y - s * _C * r
        else:
            x0 = x - s * _C * r
            y0 = y
    else:
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])

    pts: List[Tuple[float, float]] = []

    if diam == "H":
        for i in range(n + 1):
            th = math.pi * i / n
            pts.append((x0 + r * math.cos(th), y0 + s * r * math.sin(th)))
        pts.append((x0 - r, y0))
        return pts

    for i in range(n + 1):
        th = -math.pi / 2 + math.pi * i / n
        pts.append((x0 + s * r * math.cos(th), y0 + r * math.sin(th)))
    pts.append((x0, y0 - r))
    return pts


def _quarter_poly(fig: Dict, n: int = 40) -> List[Tuple[float, float]]:
    r = float(fig["raio"])
    modo = fig.get("modo_pos", "Centroide (x, y)")
    sx, sy = orient_sx_sy(fig)

    if modo.startswith("Centroide"):
        x, y = centroid_xy(fig)
        x0 = x - sx * _C * r
        y0 = y - sy * _C * r
    else:
        x0 = float(fig["x0"])
        y0 = float(fig["y0"])

    pts: List[Tuple[float, float]] = [(x0, y0)]
    for i in range(n + 1):
        th = (math.pi / 2) * i / n
        pts.append((x0 + sx * r * math.cos(th), y0 + sy * r * math.sin(th)))
    pts.append((x0, y0))
    return pts


def _add_axis_line(fig: go.Figure, x0: float, y0: float, ang_deg: float, span: float, dash: str = "solid") -> None:
    """Adiciona uma linha infinita 'cortada' pelo span, passando por (x0,y0)."""
    ang = math.radians(ang_deg)
    ux, uy = math.cos(ang), math.sin(ang)
    x1, y1 = x0 - span * ux, y0 - span * uy
    x2, y2 = x0 + span * ux, y0 + span * uy
    fig.add_shape(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=2, dash=dash))


def plot_secao(
    figs: List[Dict],
    xg: Optional[float],
    yg: Optional[float],
    alpha1_deg: Optional[float] = None,
    alpha2_deg: Optional[float] = None,
) -> go.Figure:
    fig = go.Figure()
    xs: List[float] = []
    ys: List[float] = []

    for f in figs:
        tipo = f["tipo"]
        is_furo = bool(f.get("furo", False))
        x, y = centroid_xy(f)

        fill_solid = "rgba(255,255,255,0.18)"
        fill_furo = "rgba(255,0,0,0.12)"
        fill = fill_furo if is_furo else fill_solid

        if tipo == "Retângulo":
            b = float(f["base"]); h = float(f["altura"])
            x0 = x - b / 2; x1 = x + b / 2
            y0 = y - h / 2; y1 = y + h / 2
            _bounds_update(xs, ys, [(x0, y0), (x1, y1)])
            fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(width=2), fillcolor=fill)

        elif tipo == "Círculo":
            r = float(f["raio"])
            _bounds_update(xs, ys, [(x - r, y - r), (x + r, y + r)])
            fig.add_shape(type="circle", x0=x - r, y0=y - r, x1=x + r, y1=y + r, line=dict(width=2), fillcolor=fill)

        elif tipo == "Triângulo Retângulo":
            pts = _tri_points(f)
            _bounds_update(xs, ys, pts)
            fig.add_trace(go.Scatter(
                x=[p[0] for p in pts],
                y=[p[1] for p in pts],
                mode="lines",
                fill="toself",
                fillcolor=fill,
                line=dict(width=2),
                showlegend=False,
                hoverinfo="skip",
            ))

        elif tipo == "Semicírculo":
            pts = _semi_poly(f)
            _bounds_update(xs, ys, pts)
            fig.add_trace(go.Scatter(
                x=[p[0] for p in pts],
                y=[p[1] for p in pts],
                mode="lines",
                fill="toself",
                fillcolor=fill,
                line=dict(width=2),
                showlegend=False,
                hoverinfo="skip",
            ))

        elif tipo == "Quarto de Círculo":
            pts = _quarter_poly(f)
            _bounds_update(xs, ys, pts)
            fig.add_trace(go.Scatter(
                x=[p[0] for p in pts],
                y=[p[1] for p in pts],
                mode="lines",
                fill="toself",
                fillcolor=fill,
                line=dict(width=2),
                showlegend=False,
                hoverinfo="skip",
            ))

        # centroide da figura
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers",
            marker=dict(size=9, symbol="x"),
            showlegend=False,
            hoverinfo="skip",
        ))

    # limites
    if xs and ys:
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
    else:
        minx, maxx, miny, maxy = -10, 10, -10, 10

    dx = max(1.0, (maxx - minx) * 0.15)
    dy = max(1.0, (maxy - miny) * 0.15)
    minx -= dx; maxx += dx
    miny -= dy; maxy += dy

    # eixos globais
    fig.add_shape(type="line", x0=minx, y0=0, x1=maxx, y1=0, line=dict(width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=miny, x1=0, y1=maxy, line=dict(width=1, dash="dash"))

    # centroide global
    if xg is not None and yg is not None:
        fig.add_trace(go.Scatter(
            x=[xg], y=[yg],
            mode="markers+text",
            marker=dict(size=12),
            text=["CG global"],
            textposition="top center",
            showlegend=False,
        ))

        # eixos principais
        # span grande o suficiente para cruzar o gráfico inteiro
        span = 1.2 * max(maxx - minx, maxy - miny)
        if alpha1_deg is not None:
            _add_axis_line(fig, xg, yg, alpha1_deg, span=span, dash="solid")
        if alpha2_deg is not None:
            _add_axis_line(fig, xg, yg, alpha2_deg, span=span, dash="dot")

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(range=[minx, maxx], zeroline=False, showgrid=True),
        yaxis=dict(range=[miny, maxy], zeroline=False, showgrid=True),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
