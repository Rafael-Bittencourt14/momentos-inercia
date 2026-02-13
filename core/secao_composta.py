"""Seção composta (V4)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

from .figuras import Figura
from .propriedades import ResultadosSecao


def _deg(rad: float) -> float:
    return math.degrees(rad)


@dataclass
class SecaoComposta:
    """Seção composta por figuras.

    Parâmetros:
    - unidade_comprimento: apenas metadado (ex.: "mm", "cm", "m").
      Você pode mudar manualmente no código enquanto testa.
    """
    unidade_comprimento: str = "cm"
    figuras: List[Figura] = field(default_factory=list)

    def adicionar(self, figura: Figura) -> None:
        self.figuras.append(figura)

    def limpar(self) -> None:
        self.figuras.clear()

    # -----------------------------
    # Cálculo principal
    # -----------------------------
    def calcular(
        self,
        *,
        modo: str = "quiet",
        logger: Optional[Any] = None,
    ) -> ResultadosSecao:
        """Calcula propriedades.

        modo:
          - "quiet": sem prints
          - "verbose": imprime passo a passo (didático)
        logger:
          - opcional. Se passado, registra DEBUG/INFO.
        """
        if not self.figuras:
            raise ValueError("Nenhuma figura adicionada na seção.")

        verbose = (modo.lower().strip() == "verbose")

        if logger:
            logger.debug("Iniciando cálculo: %d figuras", len(self.figuras))

        # PASSO 1: Centroide global
        soma_a = 0.0
        soma_ax = 0.0
        soma_ay = 0.0

        if verbose:
            print("\n" + "=" * 70)
            print("PASSO 1: Centroide Global")
            print("=" * 70)
            print(f"{'Fig':<5} {'Tipo':<18} {'A':>12} {'x':>10} {'y':>10} {'A*x':>12} {'A*y':>12}")
            print("-" * 70)

        for i, fig in enumerate(self.figuras, start=1):
            a = float(fig.area())
            ax = a * float(fig.x)
            ay = a * float(fig.y)

            soma_a += a
            soma_ax += ax
            soma_ay += ay

            if logger:
                logger.debug("Fig %d %s: A=%g x=%g y=%g", i, getattr(fig, "nome", "Figura"), a, fig.x, fig.y)

            if verbose:
                nome = getattr(fig, "nome", "Figura")
                print(f"{i:<5} {nome:<18} {a:>12.4f} {fig.x:>10.4f} {fig.y:>10.4f} {ax:>12.4f} {ay:>12.4f}")

        if abs(soma_a) < 1e-12:
            raise ValueError("Área total ~ 0. Verifique furos e figuras (A_total não pode ser zero).")

        xg = soma_ax / soma_a
        yg = soma_ay / soma_a

        if verbose:
            print("-" * 70)
            print(f"{'TOTAL':<5} {'':<18} {soma_a:>12.4f} {'':>10} {'':>10} {soma_ax:>12.4f} {soma_ay:>12.4f}")
            print(f"✅ Centroide: Xg = {xg:.4f} | Yg = {yg:.4f}  (unid: {self.unidade_comprimento})")

        # PASSO 2: distâncias (a, b)
        parametros: List[Tuple[Figura, float, float]] = []
        ab_rows: List[Dict[str, Any]] = []  # a=yi-Yg, b=xi-Xg (para UI/relatório)
        if verbose:
            print("\n" + "=" * 70)
            print("PASSO 2: Parâmetros a e b (distâncias ao centroide)")
            print("=" * 70)
            print(f"{'Fig':<5} {'xi':>10} {'yi':>10} {'a=yi-Yg':>12} {'b=xi-Xg':>12}")
            print("-" * 70)

        for i, fig in enumerate(self.figuras, start=1):
            a = float(fig.y) - yg
            b = float(fig.x) - xg
            parametros.append((fig, a, b))
            ab_rows.append({
                "idx": i,
                "nome": getattr(fig, "nome", "Figura"),
                "area": float(fig.area()),
                "xi": float(fig.x),
                "yi": float(fig.y),
                "a": a,
                "b": b,
            })

            if logger:
                logger.debug("Fig %d: a=%g b=%g", i, a, b)

            if verbose:
                print(f"{i:<5} {fig.x:>10.4f} {fig.y:>10.4f} {a:>12.4f} {b:>12.4f}")

        # PASSO 3: Steiner
        ix_total = 0.0
        iy_total = 0.0
        ixy_total = 0.0

        if verbose:
            print("\n" + "=" * 70)
            print("PASSO 3: Teorema de Steiner (Ix, Iy, Ixy globais)")
            print("=" * 70)
            print("Fórmulas: Ix = Ix̄ + A a² | Iy = Iȳ + A b² | Ixy = Ix̄ȳ + A a b\n")
            print(f"{'Fig':<5} {'A':>12} {'a':>10} {'b':>10} {'Ix̄':>12} {'A a²':>12} {'Ix_i':>12}")
            print("-" * 70)

        for i, (fig, a, b) in enumerate(parametros, start=1):
            A = float(fig.area())
            ix0 = float(fig.ix_proprio())
            iy0 = float(fig.iy_proprio())
            ixy0 = float(fig.ixy_proprio())

            ix = ix0 + A * a * a
            iy = iy0 + A * b * b
            ixy = ixy0 + A * a * b

            ix_total += ix
            iy_total += iy
            ixy_total += ixy

            if logger:
                logger.debug("Fig %d: Ix=%g Iy=%g Ixy=%g", i, ix, iy, ixy)

            if verbose:
                print(f"{i:<5} {A:>12.4f} {a:>10.4f} {b:>10.4f} {ix0:>12.4f} {A*a*a:>12.4f} {ix:>12.4f}")

        if verbose:
            print("-" * 70)
            print(f"✅ Ix = {ix_total:.4f} | Iy = {iy_total:.4f} | Ixy = {ixy_total:.4f}  (unid^4: {self.unidade_comprimento}⁴)")

        # PASSO 4: Eixos principais
        termo1 = (ix_total + iy_total) / 2
        termo2 = math.sqrt(((ix_total - iy_total) / 2) ** 2 + ixy_total ** 2)

        i1 = termo1 + termo2
        i2 = termo1 - termo2

        # alpha1: 0.5 * atan(2Ixy / (Iy - Ix))
        if abs(iy_total - ix_total) < 1e-12:
            alpha1 = math.pi / 4
        else:
            alpha1 = 0.5 * math.atan2(2 * ixy_total, (iy_total - ix_total))
        alpha2 = alpha1 + math.pi / 2

        if verbose:
            print("\n" + "=" * 70)
            print("PASSO 4: Eixos principais")
            print("=" * 70)
            print(f"✅ I1 = {i1:.4f} | I2 = {i2:.4f}")
            print(f"✅ α1 = {alpha1:.6f} rad ({_deg(alpha1):.2f}°)")
            print(f"✅ α2 = {alpha2:.6f} rad ({_deg(alpha2):.2f}°)")

        return ResultadosSecao(
            unidade_comprimento=self.unidade_comprimento,
            area_total=soma_a,
            xg=xg,
            yg=yg,
            ix=ix_total,
            iy=iy_total,
            ixy=ixy_total,
            i1=i1,
            i2=i2,
            alpha1_rad=alpha1,
            alpha2_rad=alpha2,
            extras={
                "alpha1_graus": _deg(alpha1),
                "alpha2_graus": _deg(alpha2),
                "unidade_area": f"{self.unidade_comprimento}²",
                "unidade_inercia": f"{self.unidade_comprimento}⁴",
                "parametros_ab": ab_rows,
                "definicao_a_b": "a = yi - Yg; b = xi - Xg"
            },
        )

    def resumo(self, resultados: ResultadosSecao) -> str:
        u = resultados.unidade_comprimento
        return (
            "\n" + "=" * 70 +
            "\nRESUMO - SEÇÃO COMPOSTA" +
            "\n" + "=" * 70 +
            f"\nÁrea total: {resultados.area_total:.4f} {u}²" +
            f"\nCentroide:  Xg={resultados.xg:.4f} {u} | Yg={resultados.yg:.4f} {u}" +
            f"\nIx={resultados.ix:.4f} {u}⁴ | Iy={resultados.iy:.4f} {u}⁴ | Ixy={resultados.ixy:.4f} {u}⁴" +
            f"\nI1={resultados.i1:.4f} {u}⁴ | I2={resultados.i2:.4f} {u}⁴" +
            f"\nα1={resultados.extras.get('alpha1_graus', 0):.2f}° | α2={resultados.extras.get('alpha2_graus', 0):.2f}°\n"
        )
