from __future__ import annotations

# --------------------------------------------------------------------
# Streamlit App — V3.0 (UX + "responsivo" + export PDF)
# --------------------------------------------------------------------
# Ajuste de PATH para o Streamlit enxergar /core e esta /interface
import sys
from pathlib import Path as _Path

ROOT = _Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INTERFACE = _Path(__file__).resolve().parent
if str(INTERFACE) not in sys.path:
    sys.path.insert(0, str(INTERFACE))

from decimal import Decimal, ROUND_HALF_DOWN
import math
from datetime import datetime
from io import BytesIO

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

from core.secao_composta import SecaoComposta

from interface.state import init_state, new_id, bump_id, reset_state_deep
from interface.adapters import dict_to_core, defaults_for, ORIENT_Q, ORIENT_SEMI
from interface.plotter import plot_secao

# PDF export (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas


# -------------------------
# Helpers
# -------------------------
def round0_half_down(x: float) -> int:
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_DOWN))


def fmt2(x: float) -> str:
    return f"{x:.2f}"


def plot_to_png_bytes(fig: go.Figure, scale: int = 2) -> bytes | None:
    """
    Converte figura Plotly para PNG em memória (requer 'kaleido').
    Retorna None se kaleido não estiver instalado.
    """
    try:
        return pio.to_image(fig, format="png", scale=scale)
    except Exception:
        return None


def principais_formulario(ix: float, iy: float, ixy: float) -> tuple[float, float, float, float]:
    """
    Convenção igual à sua planilha:
      - I1 = maior
      - I2 = menor
      - alpha2 = eixo de I2 (menor)
      - alpha1 = alpha2 - 90° (eixo de I1)
      - sinal dos ângulos compatível (planilha costuma ser horário positivo)
    """
    iavg = 0.5 * (ix + iy)
    r = math.sqrt(((ix - iy) * 0.5) ** 2 + ixy ** 2)
    I1 = iavg + r
    I2 = iavg - r

    theta_trig = 0.5 * math.atan2(-2.0 * ixy, (iy - ix))
    alpha2_trig = math.degrees(theta_trig)  # anti-horário positivo
    alpha2 = -alpha2_trig                   # planilha: horário positivo

    def norm(a: float) -> float:
        while a <= -90.0:
            a += 180.0
        while a > 90.0:
            a -= 180.0
        return a

    alpha2n = norm(alpha2)
    alpha1n = norm(alpha2n - 90.0)
    return I1, I2, alpha1n, alpha2n


def device_is_small() -> bool:
    """
    V3.0: toggle manual (sem JS).
    V3.1: podemos trocar por detecção real de largura via JS/component.
    """
    if "modo_mobile" not in st.session_state:
        st.session_state["modo_mobile"] = False
    return bool(st.session_state["modo_mobile"])


# -------------------------
# Sidebar
# -------------------------
def sidebar_controls():
    st.sidebar.title("Momentos de Inércia — V3.0")

    opcoes = ["mm", "cm", "m"]
    unidade_atual = st.session_state.get("unidade", "cm")
    idx = opcoes.index(unidade_atual) if unidade_atual in opcoes else 1
    st.session_state["unidade"] = st.sidebar.selectbox("Unidade", options=opcoes, index=idx)

    # Modo mobile (até termos detecção por largura via JS)
    st.session_state["modo_mobile"] = st.sidebar.toggle(
        "Modo celular (layout 1 coluna)",
        value=st.session_state.get("modo_mobile", False)
    )

    st.sidebar.divider()

    c1, c2 = st.sidebar.columns(2)
    if c1.button("➕ Retângulo", use_container_width=True):
        fid = new_id()
        bump_id()
        st.session_state["figs"].append(defaults_for("Retângulo", fid))

    if c2.button("➕ Círculo", use_container_width=True):
        fid = new_id()
        bump_id()
        st.session_state["figs"].append(defaults_for("Círculo", fid))

    c3, c4 = st.sidebar.columns(2)
    if c3.button("➕ Triângulo", use_container_width=True):
        fid = new_id()
        bump_id()
        st.session_state["figs"].append(defaults_for("Triângulo Retângulo", fid))

    if c4.button("➕ Semicírculo", use_container_width=True):
        fid = new_id()
        bump_id()
        st.session_state["figs"].append(defaults_for("Semicírculo", fid))

    if st.sidebar.button("➕ 1/4 Círculo", use_container_width=True):
        fid = new_id()
        bump_id()
        st.session_state["figs"].append(defaults_for("Quarto de Círculo", fid))

    st.sidebar.divider()
    st.sidebar.caption("Ações")

    if st.sidebar.button("🧹 Limpar tudo", use_container_width=True):
        reset_state_deep(manter_unidade=st.session_state.get("unidade", "cm"))
        st.rerun()


# -------------------------
# Editor de figura (UI)
# -------------------------
def editor_figura(f: dict, idx: int):
    tipo = f["tipo"]
    fid = f["id"]

    with st.expander(f"Figura #{fid} — {tipo}", expanded=(idx == 0)):
        f["furo"] = st.checkbox("Furo (subtrair)", value=bool(f.get("furo", False)), key=f"furo_{fid}")
        st.caption("Status: **FURO (subtrai)**" if f["furo"] else "Status: **Sólido**")

        if tipo == "Retângulo":
            f["base"] = st.number_input("Base", value=float(f.get("base", 10.0)), min_value=0.0, step=0.1, key=f"b_{fid}")
            f["altura"] = st.number_input("Altura", value=float(f.get("altura", 2.0)), min_value=0.0, step=0.1, key=f"h_{fid}")

            modo = st.selectbox(
                "Posição",
                ["Centroide (x, y)", "Vértice de referência (x0, y0)"],
                index=0 if f.get("modo_pos", "Centroide (x, y)").startswith("Centroide") else 1,
                key=f"modo_{fid}",
            )
            f["modo_pos"] = modo

            if modo.startswith("Centroide"):
                f["x"] = st.number_input("x (CG)", value=float(f.get("x", 0.0)), step=0.1, key=f"x_{fid}")
                f["y"] = st.number_input("y (CG)", value=float(f.get("y", 0.0)), step=0.1, key=f"y_{fid}")
            else:
                f["vertice"] = st.selectbox(
                    "Vértice",
                    ["Inferior esquerdo", "Inferior direito", "Superior esquerdo", "Superior direito"],
                    index=["Inferior esquerdo", "Inferior direito", "Superior esquerdo", "Superior direito"].index(f.get("vertice", "Inferior esquerdo")),
                    key=f"v_{fid}",
                )
                f["x0"] = st.number_input("x0 (vértice)", value=float(f.get("x0", 0.0)), step=0.1, key=f"x0_{fid}")
                f["y0"] = st.number_input("y0 (vértice)", value=float(f.get("y0", 0.0)), step=0.1, key=f"y0_{fid}")

        elif tipo == "Círculo":
            f["raio"] = st.number_input("Raio", value=float(f.get("raio", 2.0)), min_value=0.0, step=0.1, key=f"r_{fid}")
            f["modo_pos"] = "Centroide (x, y)"
            f["x"] = st.number_input("x (centro)", value=float(f.get("x", 0.0)), step=0.1, key=f"cx_{fid}")
            f["y"] = st.number_input("y (centro)", value=float(f.get("y", 0.0)), step=0.1, key=f"cy_{fid}")

        elif tipo == "Triângulo Retângulo":
            f["base"] = st.number_input("Base", value=float(f.get("base", 6.0)), min_value=0.0, step=0.1, key=f"tb_{fid}")
            f["altura"] = st.number_input("Altura", value=float(f.get("altura", 4.0)), min_value=0.0, step=0.1, key=f"th_{fid}")

            quadrantes = {
                "NE": "1º quadrante (+x, +y)",
                "NW": "2º quadrante (-x, +y)",
                "SW": "3º quadrante (-x, -y)",
                "SE": "4º quadrante (+x, -y)",
            }
            keys = list(ORIENT_Q.keys())

            def label(k: str) -> str:
                for key, lab in quadrantes.items():
                    if k.strip().upper().startswith(key):
                        return lab
                return k

            f["orientacao"] = st.selectbox(
                "Orientação (visual + sinal Ixy)",
                options=keys,
                index=keys.index(f.get("orientacao", keys[0])) if f.get("orientacao") in keys else 0,
                format_func=label,
                key=f"tori_{fid}",
            )

            modo = st.selectbox(
                "Posição",
                ["Centroide (x, y)", "Canto do ângulo reto (x0, y0)"],
                index=0 if f.get("modo_pos", "Centroide (x, y)").startswith("Centroide") else 1,
                key=f"tmodo_{fid}",
            )
            f["modo_pos"] = modo

            if modo.startswith("Centroide"):
                f["x"] = st.number_input("x (CG)", value=float(f.get("x", 0.0)), step=0.1, key=f"tx_{fid}")
                f["y"] = st.number_input("y (CG)", value=float(f.get("y", 0.0)), step=0.1, key=f"ty_{fid}")
            else:
                f["x0"] = st.number_input("x0 (ângulo reto)", value=float(f.get("x0", 0.0)), step=0.1, key=f"tx0_{fid}")
                f["y0"] = st.number_input("y0 (ângulo reto)", value=float(f.get("y0", 0.0)), step=0.1, key=f"ty0_{fid}")

        elif tipo == "Semicírculo":
            f["raio"] = st.number_input("Raio", value=float(f.get("raio", 3.0)), min_value=0.0, step=0.1, key=f"sr_{fid}")

            f["orientacao"] = st.selectbox(
                "Orientação (arco)",
                options=list(ORIENT_SEMI.keys()),
                index=list(ORIENT_SEMI.keys()).index(f.get("orientacao", list(ORIENT_SEMI.keys())[0])) if f.get("orientacao") in ORIENT_SEMI else 0,
                key=f"sori_{fid}",
            )

            modo = st.selectbox(
                "Posição",
                ["Centroide (x, y)", "Ponto médio do diâmetro (x0, y0)"],
                index=0 if f.get("modo_pos", "Centroide (x, y)").startswith("Centroide") else 1,
                key=f"smode_{fid}",
            )
            f["modo_pos"] = modo

            if modo.startswith("Centroide"):
                f["x"] = st.number_input("x (CG)", value=float(f.get("x", 0.0)), step=0.1, key=f"sx_{fid}")
                f["y"] = st.number_input("y (CG)", value=float(f.get("y", 0.0)), step=0.1, key=f"sy_{fid}")
            else:
                f["x0"] = st.number_input("x0 (meio do diâmetro)", value=float(f.get("x0", 0.0)), step=0.1, key=f"sx0_{fid}")
                f["y0"] = st.number_input("y0 (linha do diâmetro)", value=float(f.get("y0", 0.0)), step=0.1, key=f"sy0_{fid}")

        elif tipo == "Quarto de Círculo":
            f["raio"] = st.number_input("Raio", value=float(f.get("raio", 3.0)), min_value=0.0, step=0.1, key=f"qr_{fid}")

            quadrantes = {
                "NE": "1º quadrante (+x, +y)",
                "NW": "2º quadrante (-x, +y)",
                "SW": "3º quadrante (-x, -y)",
                "SE": "4º quadrante (+x, -y)",
            }
            keys = list(ORIENT_Q.keys())

            def label(k: str) -> str:
                for key, lab in quadrantes.items():
                    if k.strip().upper().startswith(key):
                        return lab
                return k

            f["orientacao"] = st.selectbox(
                "Orientação (visual + sinal Ixy)",
                options=keys,
                index=keys.index(f.get("orientacao", keys[0])) if f.get("orientacao") in keys else 0,
                format_func=label,
                key=f"qori_{fid}",
            )

            modo = st.selectbox(
                "Posição",
                ["Centroide (x, y)", "Canto (x0, y0)"],
                index=0 if f.get("modo_pos", "Centroide (x, y)").startswith("Centroide") else 1,
                key=f"qmode_{fid}",
            )
            f["modo_pos"] = modo

            if modo.startswith("Centroide"):
                f["x"] = st.number_input("x (CG)", value=float(f.get("x", 0.0)), step=0.1, key=f"qx_{fid}")
                f["y"] = st.number_input("y (CG)", value=float(f.get("y", 0.0)), step=0.1, key=f"qy_{fid}")
            else:
                f["x0"] = st.number_input("x0 (canto)", value=float(f.get("x0", 0.0)), step=0.1, key=f"qx0_{fid}")
                f["y0"] = st.number_input("y0 (canto)", value=float(f.get("y0", 0.0)), step=0.1, key=f"qy0_{fid}")

        if st.button("🗑️ Remover esta figura", key=f"rm_{fid}"):
            st.session_state["figs"].pop(idx)
            st.rerun()


# -------------------------
# PDF export
# -------------------------
def build_pdf_bytes(res_dict: dict, unidade: str, plot_png: bytes | None = None) -> bytes:
    """
    Export: 1 página A4 com resultados + tabela a/b + (opcional) imagem do plot.
    """
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    x = 20 * mm
    y = h - 20 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Momentos de Inércia — Relatório")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 10 * mm

    # Imagem do gráfico primeiro (quando existir)
    if plot_png:
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(BytesIO(plot_png))
            img_w = 170 * mm
            img_h = 95 * mm
            if y - img_h < 20 * mm:
                c.showPage()
                y = h - 20 * mm
            c.drawImage(img, x, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, anchor="sw")
            y -= (img_h + 8 * mm)
        except Exception:
            pass

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Resultados")
    y -= 8 * mm

    c.setFont("Helvetica", 10)

    lines = [
        f"Unidade: {unidade}",
        f"Área total: {res_dict['area_total']:.4f} {unidade}^2",
        f"Xg: {res_dict['xg']:.4f} {unidade}",
        f"Yg: {res_dict['yg']:.4f} {unidade}",
        "",
        f"Ix: {res_dict['ix']:.4f} {unidade}^4",
        f"Iy: {res_dict['iy']:.4f} {unidade}^4",
        f"Ixy: {res_dict['ixy']:.4f} {unidade}^4",
        "",
        f"I1 (maior): {res_dict['i1']:.4f} {unidade}^4",
        f"I2 (menor): {res_dict['i2']:.4f} {unidade}^4",
        f"α1 (eixo de I1): {res_dict['a1']:.4f}°",
        f"α2 (eixo de I2): {res_dict['a2']:.4f}°",
        "",
        "Parâmetros a e b (a = yi - Yg ; b = xi - Xg):",
    ]

    for line in lines:
        c.drawString(x, y, line)
        y -= 6.2 * mm
        if y < 20 * mm:
            c.showPage()
            y = h - 20 * mm
            c.setFont("Helvetica", 10)

    # tabela a/b
    for r in res_dict.get("ab_rows", []):
        line = (
            f"Fig #{r.get('idx')} ({r.get('nome','')}): "
            f"xi={float(r.get('xi',0.0)):.4f} {unidade} | "
            f"yi={float(r.get('yi',0.0)):.4f} {unidade} | "
            f"a={float(r.get('a',0.0)):.4f} {unidade} | "
            f"b={float(r.get('b',0.0)):.4f} {unidade}"
        )
        c.drawString(x, y, line)
        y -= 6.2 * mm
        if y < 20 * mm:
            c.showPage()
            y = h - 20 * mm
            c.setFont("Helvetica", 10)

    c.showPage()
    c.save()
    return buf.getvalue()


# -------------------------
# Resultados UI
# -------------------------
def resultados_ui(secao: SecaoComposta, unidade: str):
    res = secao.calcular(modo="quiet")

    ix = float(res.ix)
    iy = float(res.iy)
    ixy = float(res.ixy)
    I1, I2, a1, a2 = principais_formulario(ix, iy, ixy)

    ab_rows = (res.extras or {}).get("parametros_ab", [])

    st.subheader("Resultados")

    c1, c2, c3 = st.columns(3)
    c1.metric("Área total", f"{fmt2(res.area_total)} {unidade}^2")
    c2.metric("Xg", f"{fmt2(res.xg)} {unidade}")
    c3.metric("Yg", f"{fmt2(res.yg)} {unidade}")

    st.markdown("**Momentos:**")
    d1, d2, d3 = st.columns(3)
    d1.metric("Ix", f"{fmt2(ix)} {unidade}^4")
    d2.metric("Iy", f"{fmt2(iy)} {unidade}^4")
    d3.metric("Ixy", f"{fmt2(ixy)} {unidade}^4")

    st.markdown("**Eixos principais (convenção do formulário):**")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("I1 (maior)", f"{fmt2(I1)} {unidade}^4")
    p2.metric("I2 (menor)", f"{fmt2(I2)} {unidade}^4")
    p3.metric("α1 (eixo de I1)", f"{a1:.2f}°")
    p4.metric("α2 (eixo de I2)", f"{a2:.2f}°")

    st.markdown("**Parâmetros a e b (por figura):**  _a = yi − Yg ; b = xi − Xg_")
    if ab_rows:
        table = []
        for r in ab_rows:
            table.append({
                "Figura": f"#{r.get('idx')}",
                "Tipo": r.get("nome", ""),
                f"xi ({unidade})": round(float(r.get("xi", 0.0)), 2),
                f"yi ({unidade})": round(float(r.get("yi", 0.0)), 2),
                f"a ({unidade})": round(float(r.get("a", 0.0)), 2),
                f"b ({unidade})": round(float(r.get("b", 0.0)), 2),
            })
        st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.info("Ainda não há figuras suficientes para mostrar a/b.")

    with st.expander("Ver valores precisos (4 casas)"):
        st.write({
            "Área total": f"{res.area_total:.4f} {unidade}^2",
            "Xg": f"{res.xg:.4f} {unidade}",
            "Yg": f"{res.yg:.4f} {unidade}",
            "Ix": f"{ix:.4f} {unidade}^4",
            "Iy": f"{iy:.4f} {unidade}^4",
            "Ixy": f"{ixy:.4f} {unidade}^4",
            "I1 (maior)": f"{I1:.4f} {unidade}^4",
            "I2 (menor)": f"{I2:.4f} {unidade}^4",
            "α1": f"{a1:.4f}°",
            "α2": f"{a2:.4f}°",
            "a/b (por figura)": ab_rows,
        })

    export_dict = {
        "area_total": float(res.area_total),
        "xg": float(res.xg),
        "yg": float(res.yg),
        "ix": ix, "iy": iy, "ixy": ixy,
        "i1": I1, "i2": I2,
        "a1": a1, "a2": a2,
        "ab_rows": ab_rows,
    }
    return float(res.xg), float(res.yg), a1, a2, export_dict


# -------------------------
# Main
# -------------------------
def main():
    st.set_page_config(page_title="Momentos de Inércia", layout="wide")
    init_state()
    sidebar_controls()

    figs = st.session_state.get("figs", [])
    unidade = st.session_state.get("unidade", "cm")
    mobile = device_is_small()

    # Layout mobile (1 coluna)
    if mobile:
        st.header("Dados")
        if figs:
            for i, f in enumerate(figs):
                editor_figura(f, i)
        else:
            st.info("Use a barra lateral para adicionar figuras.")

        st.header("Visualização")

        if figs:
            secao = SecaoComposta(unidade_comprimento=unidade)
            for f in figs:
                secao.adicionar(dict_to_core(f))

            xg, yg, a1, a2, export_dict = resultados_ui(secao, unidade)

            fig_plot = plot_secao(figs, xg, yg, alpha1_deg=a1, alpha2_deg=a2)
            st.plotly_chart(fig_plot, use_container_width=True)

            # gera imagem do gráfico "atual" para o PDF
            plot_png = plot_to_png_bytes(fig_plot, scale=2)
            pdf_bytes = build_pdf_bytes(export_dict, unidade, plot_png=plot_png)

            st.download_button(
                "⬇️ Exportar resultados (PDF)",
                data=pdf_bytes,
                file_name="momentos_inercia_resultados.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.plotly_chart(plot_secao([], None, None), use_container_width=True)
            st.subheader("Resultados")
            st.write("—")
        return

    # Layout desktop (2 colunas)
    col_dados, col_vis = st.columns([1.15, 1.0], gap="large")

    with col_dados:
        st.header("Dados")
        if figs:
            for i, f in enumerate(figs):
                editor_figura(f, i)
        else:
            st.info("Use a barra lateral para adicionar figuras.")

    with col_vis:
        st.header("Visualização")
        if figs:
            secao = SecaoComposta(unidade_comprimento=unidade)
            for f in figs:
                secao.adicionar(dict_to_core(f))

            xg, yg, a1, a2, export_dict = resultados_ui(secao, unidade)

            fig_plot = plot_secao(figs, xg, yg, alpha1_deg=a1, alpha2_deg=a2)
            st.plotly_chart(fig_plot, use_container_width=True)

            plot_png = plot_to_png_bytes(fig_plot, scale=2)
            pdf_bytes = build_pdf_bytes(export_dict, unidade, plot_png=plot_png)

            st.download_button(
                "⬇️ Exportar resultados (PDF)",
                data=pdf_bytes,
                file_name="momentos_inercia_resultados.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.plotly_chart(plot_secao([], None, None), use_container_width=True)
            st.subheader("Resultados")
            st.write("—")


if __name__ == "__main__":
    main()
